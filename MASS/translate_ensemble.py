# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
#
# Translate sentences from the input stream.
# The model will be faster is sentences are sorted by length.
# Input sentences must have the same tokenization and BPE codes than the ones used in the model.
# It also supports ensemble multiple models, beam search and length penlty.
#
# Usage:
#     cat source_sentences.bpe | \
#     python translate.py --exp_name translate \
#     --exp_id en-fr \
#     --src_lang en --tgt_lang fr \
#     --model_path model1.pth,model2.pth --output_path output \
#     --beam 10 --length_penalty 1.1
#

import os
import io
import sys
import argparse
import torch
import math
import torch.nn as nn
import torch.nn.functional as F

from collections import OrderedDict

from src.utils import AttrDict
from src.utils import bool_flag, initialize_exp
from src.data.dictionary import Dictionary
from src.model.transformer import TransformerModel
from src.model.transformer import BeamHypotheses

from src.fp16 import network_to_half


def get_parser():
    """
    Generate a parameters parser.
    """
    # parse parameters
    parser = argparse.ArgumentParser(description="Translate sentences")

    # main parameters
    parser.add_argument("--dump_path", type=str, default="./dumped/", help="Experiment dump path")
    parser.add_argument("--exp_name", type=str, default="", help="Experiment name")
    parser.add_argument("--exp_id", type=str, default="", help="Experiment ID")
    parser.add_argument("--fp16", type=bool_flag, default=False, help="Run model with float16")
    parser.add_argument("--batch_size", type=int, default=32, help="Number of sentences per batch")
    parser.add_argument("--num_lines", type=int, default=1000, help="Number of sentences to translate")

    # model / output paths
    parser.add_argument("--model_path", type=str, default="", help="Model path")
    parser.add_argument("--output_path", type=str, default="", help="Output path")
    
    parser.add_argument("--beam", type=int, default=1, help="Beam size")
    parser.add_argument("--length_penalty", type=float, default=1, help="length penalty")

    # source language / target language
    parser.add_argument("--src_lang", type=str, default="", help="Source language")
    parser.add_argument("--tgt_lang", type=str, default="", help="Target language")

    # sampling method
    parser.add_argument("--uni_sampling", action='store_true', help='Activite to use uniform sampling instead of a beam search.')
    parser.add_argument("--samples_per_source", type=int, default=1, help='Number of samples per source sentece.')
    parser.add_argument("--temperature", type=float, default=1., help='Softmax temperature. Relevant for uniform sampling onnly.')
    parser.add_argument("--p", type=float, default=0., help='P for top-p sampling.')
    parser.add_argument("--k", type=int, default=0, help='K for top-k sampling.')

    return parser

def top_k_top_p_filtering(logits, top_k=0, top_p=0.0, filter_value=-float('Inf')):
    """ Filter a distribution of logits using top-k and/or nucleus (top-p) filtering
            Args:
                logits: logits distribution shape (vocabulary size)
                top_k >0: keep only top k tokens with highest probability (top-k filtering).
                top_p >0.0: keep the top tokens with cumulative probability >= top_p (nucleus filtering).
                    Nucleus filtering is described in Holtzman et al. (http://arxiv.org/abs/1904.09751)
    """
    # code was taken from
    assert logits.dim() == 1  # batch size 1 for now - could be updated for more but the code would be less clear
    top_k = min(top_k, logits.size(-1))  # Safety check
    if top_k > 0:
        # Remove all tokens with a probability less than the last token of the top-k
        indices_to_remove = logits < torch.topk(logits, top_k)[0][..., -1, None]
        logits[indices_to_remove] = filter_value
    if top_p > 0.0:
        sorted_logits, sorted_indices = torch.sort(logits, descending=True)
        cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
        # Remove tokens with cumulative probability above the threshold
        sorted_indices_to_remove = cumulative_probs > top_p
        # Shift the indices to the right to keep also the first token above the threshold
        sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
        sorted_indices_to_remove[..., 0] = 0
        indices_to_remove = sorted_indices[sorted_indices_to_remove]
        logits[indices_to_remove] = filter_value
    return logits

def generate_uni_sample(decoders, src_encodeds, src_len, tgt_lang_id, beam_size, length_penalty, early_stopping, max_len=200, params=None):
    assert params is not None

    beam_size = 1 # override since there is no beam
    bs = len(src_len)
    n_words = params.n_words

    src_len = src_len.unsqueeze(1).expand(bs, beam_size).contiguous().view(-1)
    for i in range(len(src_encodeds)):
        src_encodeds[i] = src_encodeds[i].unsqueeze(1).expand(
            (bs, beam_size) + src_encodeds[i].shape[1:]).contiguous().view(
            (bs * beam_size,) + src_encodeds[i].shape[1:])


    # generated will hold the geerated titles, init wis the pad index and <eos> at the start of each sample
    generated = src_len.new(max_len, bs * beam_size) # [max_len, bs]
    generated.fill_(params.pad_index)
    generated[0].fill_(params.eos_index)

    # generated_hyps = [BeamHypotheses(beam_size, max_len, length_penalty, early_stopping) for _ in range(bs)]

    positions = src_len.new(max_len).long() # holds the position for each index (for transformer block) [max_len, 2]
    positions = torch.arange(max_len, out=positions).unsqueeze(1).expand_as(generated)

    langs = positions.clone().fill_(tgt_lang_id)
    # beam_scores = src_encodeds[0].new(bs, beam_size).fill_(0)
    # beam_scores[:, 1:] = -1e9
    # beam_scores = beam_scores.view(-1)

    cur_len = 1
    caches = [{'slen': 0} for i in range(len(decoders))]
    done = [False for _ in range(bs)]
    tgt_len = src_len.new(bs).fill_(max_len)

    decoded = src_len.new(1, bs).fill_(params.eos_index)

    while cur_len < max_len:
        avg_scores = []
        # avg_scores = None
        for i, (src_enc, decoder) in enumerate(zip(src_encodeds, decoders)):
            tensor = decoder.forward(
                'fwd',
                x=generated[:cur_len],
                lengths=src_len.new(bs * beam_size).fill_(cur_len),
                positions=positions[:cur_len],
                langs=langs[:cur_len],
                causal=True,
                src_enc=src_enc,
                src_len=src_len,
                cache=caches[i]
            )
            assert tensor.size() == (1, bs * beam_size, decoder.dim)
            tensor = tensor.data[-1, :, :]  # (bs * beam_size, dim)
            scores = decoder.pred_layer.get_scores(tensor)  # (bs * beam_size, n_words)
            scores = scores / params.temperature  # (bs * beam_size, n_words)
            for sample_i in range(scores.size()[0]):
                scores[sample_i] = top_k_top_p_filtering(scores[sample_i], top_k=params.k, top_p=params.p) # k = 0 -> no top k
            probs = F.softmax(scores, dim=-1)  # (bs * beam_size, n_words)
            samples = torch.multinomial(probs, 1).t()

            for i in range(bs):
                if done[i]:
                    samples[0, i] = params.pad_index

            generated[cur_len] = samples # update generated
            decoded = torch.cat((decoded,samples),0) # add samples


            # re-order batch and internal states
            # generated = generated[:, beam_idx]
            # generated[cur_len] = beam_words
            for cache in caches:
                for k in cache.keys():
                    if k != 'slen':
                        cache[k] = (cache[k][0], cache[k][1])

            # mark done
            for sent_id in range(bs):

                is_eos = bool(decoded[cur_len][sent_id] == params.eos_index)

                if is_eos and not done[sent_id]:
                    tgt_len[sent_id] = cur_len + 1

                done[sent_id] = done[sent_id] or is_eos

        # exit if all done
        if all(done):
            break

        # update current length
        cur_len = cur_len + 1

    # end unfinished sentences
    for sent_id in range(bs):
        if not done[sent_id]:
            decoded[-1][sent_id] = params.eos_index


    # sanity check
    assert (decoded == params.eos_index).sum() == 2 * bs # check that you have 2 eos tokes per sentence

    return decoded, tgt_len


def generate_beam(decoders, src_encodeds, src_len, tgt_lang_id, beam_size, length_penalty, early_stopping, max_len=200, params=None):
    assert params is not None

    src_encs = []

    bs = len(src_len)
    n_words = params.n_words
    
    src_len = src_len.unsqueeze(1).expand(bs, beam_size).contiguous().view(-1)
    for i in range(len(src_encodeds)):
        src_encodeds[i] = src_encodeds[i].unsqueeze(1).expand((bs, beam_size) + src_encodeds[i].shape[1:]).contiguous().view((bs * beam_size,) + src_encodeds[i].shape[1:])
        
    generated = src_len.new(max_len, bs * beam_size)
    generated.fill_(params.pad_index)
    generated[0].fill_(params.eos_index) 
    
    generated_hyps = [BeamHypotheses(beam_size, max_len, length_penalty, early_stopping) for _ in range(bs)]

    positions = src_len.new(max_len).long()
    positions = torch.arange(max_len, out=positions).unsqueeze(1).expand_as(generated)

    langs = positions.clone().fill_(tgt_lang_id)
    beam_scores = src_encodeds[0].new(bs, beam_size).fill_(0)
    beam_scores[:, 1:] = -1e9
    beam_scores = beam_scores.view(-1)
    
    cur_len = 1
    caches = [{'slen': 0} for i in range(len(decoders))]
    done = [False for _ in range(bs)]

    while cur_len < max_len:
        avg_scores = []
        #avg_scores = None
        for i, (src_enc, decoder) in enumerate(zip(src_encodeds, decoders)):
            tensor = decoder.forward(
                'fwd',
                x=generated[:cur_len],
                lengths=src_len.new(bs * beam_size).fill_(cur_len),
                positions=positions[:cur_len],
                langs=langs[:cur_len],
                causal=True,
                src_enc=src_enc,
                src_len=src_len,
                cache=caches[i]
            )
            assert tensor.size() == (1, bs * beam_size, decoder.dim)
            tensor = tensor.data[-1, :, :]               # (bs * beam_size, dim)
            scores = decoder.pred_layer.get_scores(tensor)  # (bs * beam_size, n_words)
            scores = F.log_softmax(scores, dim=-1)       # (bs * beam_size, n_words)
            
            avg_scores.append(scores)
        
        avg_scores = torch.logsumexp(torch.stack(avg_scores, dim=0), dim=0) - math.log(len(decoders))
        #avg_scores.div_(len(decoders))
        _scores = avg_scores + beam_scores[:, None].expand_as(avg_scores)
        _scores = _scores.view(bs, beam_size * n_words)
        next_scores, next_words = torch.topk(_scores, 2 * beam_size, dim=1, largest=True, sorted=True)
        assert next_scores.size() == next_words.size() == (bs, 2 * beam_size)
        
        next_batch_beam = []

        for sent_id in range(bs):

            # if we are done with this sentence
            done[sent_id] = done[sent_id] or generated_hyps[sent_id].is_done(next_scores[sent_id].max().item())
            if done[sent_id]:
                next_batch_beam.extend([(0, params.pad_index, 0)] * beam_size)  # pad the batch
                continue

            # next sentence beam content
            next_sent_beam = []

            # next words for this sentence
            for idx, value in zip(next_words[sent_id], next_scores[sent_id]):

                # get beam and word IDs
                beam_id = idx // n_words
                word_id = idx % n_words

                # end of sentence, or next word
                if word_id == params.eos_index or cur_len + 1 == max_len:
                    generated_hyps[sent_id].add(generated[:cur_len, sent_id * beam_size + beam_id].clone(), value.item())
                else:
                    next_sent_beam.append((value, word_id, sent_id * beam_size + beam_id))

                # the beam for next step is full
                if len(next_sent_beam) == beam_size:
                    break

            # update next beam content
            assert len(next_sent_beam) == 0 if cur_len + 1 == max_len else beam_size
            if len(next_sent_beam) == 0:
                next_sent_beam = [(0, params.pad_index, 0)] * beam_size  # pad the batch
            next_batch_beam.extend(next_sent_beam)
            assert len(next_batch_beam) == beam_size * (sent_id + 1)

        # sanity check / prepare next batch
        assert len(next_batch_beam) == bs * beam_size
        beam_scores = beam_scores.new([x[0] for x in next_batch_beam])
        beam_words = generated.new([x[1] for x in next_batch_beam])
        beam_idx = src_len.new([x[2] for x in next_batch_beam])

        # re-order batch and internal states
        generated = generated[:, beam_idx]
        generated[cur_len] = beam_words
        for cache in caches:
            for k in cache.keys():
                if k != 'slen':
                    cache[k] = (cache[k][0][beam_idx], cache[k][1][beam_idx])

        # update current length
        cur_len = cur_len + 1

        # stop when we are done with each sentence
        if all(done):
            break

    tgt_len = src_len.new(bs)
    best = []

    for i, hypotheses in enumerate(generated_hyps):
        best_hyp = max(hypotheses.hyp, key=lambda x: x[0])[1]
        tgt_len[i] = len(best_hyp) + 1  # +1 for the <EOS> symbol
        best.append(best_hyp)

    # generate target batch
    decoded = src_len.new(tgt_len.max().item(), bs).fill_(params.pad_index)
    for i, hypo in enumerate(best):
        decoded[:tgt_len[i] - 1, i] = hypo
        decoded[tgt_len[i] - 1, i] = params.eos_index

    # sanity check
    assert (decoded == params.eos_index).sum() == 2 * bs

    return decoded, tgt_len


def main(params):

    # initialize the experiment
    logger = initialize_exp(params)
    parser = get_parser()
    params = parser.parse_args()
    models_path = params.model_path.split(',')

    #choose device
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    map_location = {'cuda:0': 'cpu'} if not torch.cuda.is_available() else None

    # generate parser / parse parameters
    models_reloaded = []
    for model_path in models_path:
        # models_reloaded.append(torch.load(model_path))
        models_reloaded.append(torch.load(model_path, map_location=map_location))
    model_params = AttrDict(models_reloaded[0]['params'])
    logger.info("Supported languages: %s" % ", ".join(model_params.lang2id.keys()))

    # update dictionary parameters
    for name in ['n_words', 'bos_index', 'eos_index', 'pad_index', 'unk_index', 'mask_index']:
        setattr(params, name, getattr(model_params, name))

    # build dictionary / build encoder / build decoder / reload weights
    dico = Dictionary(models_reloaded[0]['dico_id2word'], models_reloaded[0]['dico_word2id'], models_reloaded[0]['dico_counts'])
    params.src_id = model_params.lang2id[params.src_lang]
    params.tgt_id = model_params.lang2id[params.tgt_lang]

    encoders = []
    decoders = []

    def package_module(modules):
        state_dict = OrderedDict()
        for k, v in modules.items():
            if k.startswith('module.'):
                state_dict[k[7:]] = v
            else:
                state_dict[k] = v
        return state_dict

    for reloaded in models_reloaded:
        encoder = TransformerModel(model_params, dico, is_encoder=True, with_output=True).to(device).eval()
        decoder = TransformerModel(model_params, dico, is_encoder=False, with_output=True).to(device).eval()
        encoder.load_state_dict(package_module(reloaded['encoder']))
        decoder.load_state_dict(package_module(reloaded['decoder']))

        # float16
        if params.fp16:
            assert torch.backends.cudnn.enabled
            encoder = network_to_half(encoder)
            decoder = network_to_half(decoder)

        encoders.append(encoder)
        decoders.append(decoder)
    
    # src_sent = ['Poly@@ gam@@ ie statt Demokratie .']
    # src_sent += ['Trump was born and raised in the New York City borough of Queens, and received an economics degree from the Wharton School. He took charge of his familys real estate business in 1971, renamed it The Trump Organization, and expanded it from Queens and Brooklyn into Manhattan.']
    src_sent = []
    for line in sys.stdin.readlines():
        assert len(line.strip().split()) > 0
        src_sent +=[line] * params.samples_per_source

    f = io.open(params.output_path, 'w', encoding='utf-8')

    for i in range(0, len(src_sent), params.batch_size):

        # prepare batch
        word_ids = [torch.LongTensor([dico.index(w) for w in s.strip().split()])
                    for s in src_sent[i:i + params.batch_size]]
        lengths = torch.LongTensor([len(s) + 2 for s in word_ids])
        batch = torch.LongTensor(lengths.max().item(), lengths.size(0)).fill_(params.pad_index)
        batch[0] = params.eos_index
        for j, s in enumerate(word_ids):
            if lengths[j] > 2:  # if sentence not empty
                batch[1:lengths[j] - 1, j].copy_(s)
            batch[lengths[j] - 1, j] = params.eos_index
        langs = batch.clone().fill_(params.src_id)

        # encode source batch and translate it
        encodeds = []
        for encoder in encoders:
            encoded = encoder('fwd', x=batch.to(device), lengths=lengths.to(device), langs=langs.to(device), causal=False)
            encoded = encoded.transpose(0, 1)
            encodeds.append(encoded)

            assert encoded.size(0) == lengths.size(0)

        gen_func = generate_uni_sample if params.uni_sampling else generate_beam
        decoded, dec_lengths = gen_func(decoders, encodeds, lengths.to(device), params.tgt_id,
                      beam_size=params.beam,
                      length_penalty=params.length_penalty,
                      early_stopping=False,
                      max_len= 15 + 2, #int(1.5 * lengths.max().item() + 10),
                      params=params)

        # convert sentences to words
        for j in range(decoded.size(1)): # for each sentence in batch

            # remove delimiters
            sent = decoded[:, j]
            delimiters = (sent == params.eos_index).nonzero().view(-1)
            assert len(delimiters) >= 1 and delimiters[0].item() == 0
            sent = sent[1:] if len(delimiters) == 1 else sent[1:delimiters[1]]

            # output translation
            source = src_sent[i + j].strip()
            target = " ".join([dico[sent[k].item()] for k in range(len(sent))])
            sys.stderr.write("%i / %i: %s -> %s\n" % (i + j, len(src_sent), source, target))
            f.write(target + "\n")

    f.close()


if __name__ == '__main__':

    # generate parser / parse parameters
    parser = get_parser()
    params = parser.parse_args()

    # check parameters
    #assert os.path.isfile(params.model_path)
    assert params.src_lang != '' and params.tgt_lang != '' and params.src_lang != params.tgt_lang
    assert params.output_path and not os.path.isfile(params.output_path)

    # translate
    with torch.no_grad():
        main(params)
