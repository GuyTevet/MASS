TEMPS=($(seq 0.2 0.01 1.21))
line=1
for t in "${TEMPS[@]}"; do
        bash eval_storygen_single_line.sh -t $t -l $line
        ((line++))
    done
