TEMP=1.0
MODEL=./dumped/copy_mass_storygen/njydvj0mp7/checkpoint.pth

while getopts s:t: option
do
    case "${option}"
        in
        t) TEMP=${OPTARG};;
    esac
done

if [ ! -e "./eval" ]; then
    mkdir eval
fi

OUTPATH=./eval/output.storygen.temp${TEMP}

python train.py                                      \
--exp_name storygenn_test                        \
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
--eval_bleu true                                     \
--english_only true                                  \
--reload_model "$MODEL,$MODEL"			     \
--softmax_temperature $TEMP \
--eval_only true \
--eval_output $OUTPATH  \

