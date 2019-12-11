TEMPS=($(seq 0.2 0.01 1.21))

for t in "${TEMPS[@]}"; do
        bash eval_storygen.sh -t $t
    done
