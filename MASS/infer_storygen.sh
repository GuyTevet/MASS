SAMPLES=10
TEMP=1.

while getopts s:t: option
do
    case "${option}"
        in
        s) SAMPLES=${OPTARG};;
        t) TEMP=${OPTARG};;
    esac
done

OUTPATH=./infer/output.storygen.uni.sample${SAMPLES}.temp${TEMP}

python translate_ensemble.py \
--exp_name giga_test \
--src_lang ar --tgt_lang ti \
--beam 5 \
--batch_size 32 \
--model_path ./dumped/copy_mass_storygen/s9mhqgpg49/checkpoint.pth \
--output_path $OUTPATH < ./data/processed/giga/test.ar-ti.ar \
--uni_sampling \
--samples_per_source $SAMPLES \
--temperature $TEMP 

sed -i -r 's/(@@ )|(@@ ?$)//g' $OUTPATH
