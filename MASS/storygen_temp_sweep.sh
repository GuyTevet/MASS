
SAMPLES=10
#TEMPS=(
#    0.1 0.2 0.5 0.8 1 1.1 1.2 1.4 1.6
#    )
TEMPS=($(seq 0.2 0.01 1.21))

for t in "${TEMPS[@]}"; do
        bash infer_storygen.sh -s $SAMPLES -t $t
    done
