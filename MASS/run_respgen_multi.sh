# MODEL=mass_en_1024.pth
MODEL=mass_summarization_1024.pth

export NGPU=2
CUDA_VISIBLE_DEVICES=0,3

python -m torch.distributed.launch --nproc_per_node=$NGPU train.py                                      \
--exp_name mass_respgen_lowercase                        \
--data_path ./data/processed/cmdc/                   \
--lgs 'ra-rb'                                        \
--mt_steps 'ra-rb'                                  \
--encoder_only false                                 \
--emb_dim 1024                                       \
--n_layers 6                                         \
--n_heads 8                                          \
--dropout 0.2                                        \
--attention_dropout 0.2                              \
--gelu_activation true                               \
--tokens_per_batch 3000                              \
--optimizer adam_inverse_sqrt,beta1=0.9,beta2=0.98,lr=0.0001 \
--epoch_size 200000                                  \
--max_epoch 30                                       \
--eval_bleu true                                     \
--english_only true                                  \
--reload_model "$MODEL,$MODEL"
