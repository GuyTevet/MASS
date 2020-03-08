
SAMPLES=10
KS_FILE=logspace_1_32k_101.txt

cat $KS_FILE | while read k 
do
    bash infer_reddit_dialog_topk.sh -s $SAMPLES -k $k
done
