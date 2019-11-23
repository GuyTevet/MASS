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

if [ ! -e "./infer" ]; then
    mkdir infer
fi

OUTPATH=./infer/output.storygen_lower.uni.sample${SAMPLES}.temp${TEMP}

python translate_ensemble.py \
--exp_name giga_test \
--src_lang sa --tgt_lang sb \
--beam 5 \
--batch_size 32 \
--model_path ./dumped/copy_mass_storygen_lowercase/ra58l37ahd/checkpoint.pth \
--output_path $OUTPATH < ./data/processed/rocs/test.sa-sb.sa \
--uni_sampling \
--samples_per_source $SAMPLES \
--temperature $TEMP 

sed -i -r 's/(@@ )|(@@ ?$)//g' $OUTPATH
