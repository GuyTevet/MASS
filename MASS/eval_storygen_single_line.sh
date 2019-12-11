TEMP=1.0
LINE=1
MODEL=./dumped/copy_mass_storygen/njydvj0mp7/checkpoint.pth

while getopts l:t: option
do
    case "${option}"
        in
        t) TEMP=${OPTARG};;
        l) LINE=${OPTARG};;
    esac
done

if [ ! -e "./eval" ]; then
    mkdir eval
fi

OUTPATH=./eval_single_line/output.storygen.temp${TEMP}
mkdir ./eval_single_line/

python train.py                                      \
--exp_name storygenn_test                        \
--data_path ./data/processed/rocs_single_line/line_${LINE} \
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

