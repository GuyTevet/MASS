SAMPLES=10
K=0

while getopts s:k: option
do
    case "${option}"
        in
        s) SAMPLES=${OPTARG};;
        k) K=${OPTARG};;
    esac
done

DIR=./infer_storygen_topk

if [ ! -e $DIR ]; then
    mkdir $DIR
fi

OUTPATH=./${DIR}/output.storygen.uni.sample${SAMPLES}.topk${K}

python translate_ensemble.py \
--exp_name giga_test \
--src_lang sa --tgt_lang sb \
--beam 5 \
--batch_size 32 \
--model_path ./dumped/copy_mass_storygen/njydvj0mp7/checkpoint.pth \
--output_path $OUTPATH < ./data/processed/rocs/test.sa-sb.sa \
--uni_sampling \
--samples_per_source $SAMPLES \
--temperature 1.0 \
--k $K

sed -i -r 's/(@@ )|(@@ ?$)//g' $OUTPATH
