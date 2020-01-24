SAMPLES=10
TEMP=1.0

while getopts s:t: option
do
    case "${option}"
        in
        s) SAMPLES=${OPTARG};;
        t) TEMP=${OPTARG};;
    esac
done

DIR=infer_reddit

if [ ! -e $DIR ]; then
    mkdir $DIR
fi

OUTPATH=./${DIR}/output.reddit.uni.sample${SAMPLES}.temp${TEMP}

python translate_ensemble.py \
--exp_name giga_test \
--src_lang ca --tgt_lang cb \
--beam 5 \
--batch_size 32 \
--model_path ./dumped/mass_reddit_dialog/bih7q9ocyz/checkpoint.pth \
--output_path $OUTPATH < ./data/processed/reddit/test.ca-cb.sa \
--uni_sampling \
--samples_per_source $SAMPLES \
--temperature $TEMP 

sed -i -r 's/(@@ )|(@@ ?$)//g' $OUTPATH
