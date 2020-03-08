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

DIR=infer_reddit_topk

if [ ! -e $DIR ]; then
    mkdir $DIR
fi

OUTPATH=./${DIR}/output.reddit.uni.sample${SAMPLES}.topk${K}

python translate_ensemble.py \
--exp_name giga_test \
--src_lang ca --tgt_lang cb \
--beam 5 \
--batch_size 32 \
--model_path ./dumped/mass_reddit_dialog/bih7q9ocyz/checkpoint.pth \
--output_path $OUTPATH < ./data/processed/reddit/test.ca-cb.ca \
--uni_sampling \
--samples_per_source $SAMPLES \
--temperature 1.0 \
--k $K 

sed -i -r 's/(@@ )|(@@ ?$)//g' $OUTPATH
