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

python translate_ensemble.py \
--exp_name giga_test \
--src_lang ar --tgt_lang ti \
--beam 5 \
--batch_size 32 \
--model_path ./dumped/copy_mass_summarization/qtfpweuu4d/checkpoint.pth \
--output_path ./infer/output.txt.uni.sample${SAMPLES}.temp${TEMP} < ./data/processed/giga/test.ar-ti.ar \
--uni_sampling \
--samples_per_source $SAMPLES \
--temperature $TEMP \
