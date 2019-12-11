#!/usr/bin/env bash

MAIN_PATH=$PWD
DATA_PATH=$PWD/data
PROC_PATH=$DATA_PATH/processed/rocs/ # path to the already process full dataset
OUT_PATH=$DATA_PATH/processed/rocs_single_line/ # path to dir where single line dataset will be created
FULL_VOCAB=$PROC_PATH/vocab.sa-sb

mkdir -p $OUT_PATH

TRAIN_SRC_BPE=$PROC_PATH/train.sa-sb.sa
TRAIN_TGT_BPE=$PROC_PATH/train.sa-sb.sb
VALID_SRC_BPE=$PROC_PATH/valid.sa-sb.sa
VALID_TGT_BPE=$PROC_PATH/valid.sa-sb.sb
TEST_SRC_BPE=$PROC_PATH/test.sa-sb.sa
TEST_TGT_BPE=$PROC_PATH/test.sa-sb.sb

# count lines in test / validation set
TEST_LINES="$(cat $TEST_SRC_BPE | wc -l)"
echo "Found [$TEST_LINES] lines in set [$TEST_SRC_BPE]"
VALID_LINES="$(cat $VALID_SRC_BPE | wc -l)"
echo "Found [$VALID_LINES] lines in set [$VALID_SRC_BPE]"

# create single line TEST set (assuming test set smaller or equal to validation set)
for i in $(seq 1 $TEST_LINES)
do
    TARGET_PATH=$OUT_PATH/line_$i
    mkdir $TARGET_PATH

    TRAIN_LINE_SRC_BPE=$TARGET_PATH/train.sa-sb.sa
    TRAIN_LINE_TGT_BPE=$TARGET_PATH/train.sa-sb.sb
    VALID_LINE_SRC_BPE=$TARGET_PATH/valid.sa-sb.sa
    VALID_LINE_TGT_BPE=$TARGET_PATH/valid.sa-sb.sb
    TEST_LINE_SRC_BPE=$TARGET_PATH/test.sa-sb.sa
    TEST_LINE_TGT_BPE=$TARGET_PATH/test.sa-sb.sb

    # copy single line from each dataset to the target dir
    sed "${i}q;d" $VALID_SRC_BPE >> $VALID_LINE_SRC_BPE
    sed "${i}q;d" $VALID_TGT_BPE >> $VALID_LINE_TGT_BPE
    sed "${i}q;d" $TEST_SRC_BPE >> $TEST_LINE_SRC_BPE
    sed "${i}q;d" $TEST_TGT_BPE >> $TEST_LINE_TGT_BPE

    # generate .pth files
    python $MAIN_PATH/preprocess.py $FULL_VOCAB $VALID_LINE_SRC_BPE
    python $MAIN_PATH/preprocess.py $FULL_VOCAB $VALID_LINE_TGT_BPE
    python $MAIN_PATH/preprocess.py $FULL_VOCAB $TEST_LINE_SRC_BPE
    python $MAIN_PATH/preprocess.py $FULL_VOCAB $TEST_LINE_TGT_BPE

    # copy validation to train set (just as a place holder! this data is for evaluation only)
    cp ${VALID_SRC_BPE}.pth ${TRAIN_LINE_SRC_BPE}.pth
    cp ${VALID_SRC_BPE}.pth ${TRAIN_LINE_SRC_BPE}.pth

done




