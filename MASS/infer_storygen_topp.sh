SAMPLES=10
P=1.0

while getopts s:p: option
do
    case "${option}"
        in
        s) SAMPLES=${OPTARG};;
        p) P=${OPTARG};;
    esac
done

DIR=./infer_storygen_topp

if [ ! -e $DIR ]; then
    mkdir $DIR
fi

OUTPATH=./${DIR}/output.storygen.uni.sample${SAMPLES}.topp${P}

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
--p $P

sed -i -r 's/(@@ )|(@@ ?$)//g' $OUTPATH
