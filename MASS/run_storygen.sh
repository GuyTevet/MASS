# MODEL=mass_en_1024.pth
MODEL=mass_summarization_1024.pth

python train.py                                      \
--exp_name mass_storygen                        \
--data_path ./data/processed/rocs/                   \
--lgs 'sa-sb'                                        \
--mt_steps 'sa-sb'                                  \
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
