python translate_ensemble.py \
--exp_name giga_test \
--src_lang ar --tgt_lang ti \
--beam 5 \
--batch_size 1 \
--model_path ./dumped/copy_mass_summarization/qtfpweuu4d/checkpoint.pth --output_path ./infer/output.txt.beam5 < ./data/processed/giga/test.ar-ti.ar
