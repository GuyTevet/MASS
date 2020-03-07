
SAMPLES=10
PS=($(seq 0.1 0.009 1.0))

for p in "${PS[@]}"; do
        bash infer_reddit_dialog_topp.sh -s $SAMPLES -p $p
    done
