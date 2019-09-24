
SAMPLES=10
TEMPS=(
    0.2 0.5 0.8 1 1.1 1.2 1.4
    )

for t in "${TEMPS[@]}"; do
        bash run_infer.sh -s $SAMPLES -t $t
    done
