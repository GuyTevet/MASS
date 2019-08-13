
SAMPLES=10
TEMPS=(
    .2 .5 .8 1. 2. 4.
    )

for t in "${TEMPS[@]}"; do
        echo '[[[run temp ${t}]]]'
        bash run_infer.sh -s $SAMPLES -t $t
    done
