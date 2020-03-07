
SAMPLES=10
#TEMPS=(
#    0.1 0.2 0.5 0.8 1 1.1 1.2 1.4 1.6
#    )
PS=($(seq 0.1 0.009 1.0))

for p in "${PS[@]}"; do
        bash infer_storygen_topp.sh -s $SAMPLES -p $p
    done
