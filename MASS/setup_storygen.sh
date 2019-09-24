rocs=ROCStories # the path of your roc stories dataset

# install tools
if [ ! -e "./tools" ]; then
    echo "== Installing Tools =="
    bash install-tools.sh
fi

# download vocab + codes
if [ ! -e "./vocab_en" ]; then
    echo "== Download vocab + codes =="
    wget "https://modelrelease.blob.core.windows.net/mass/vocab_en"
    wget "https://modelrelease.blob.core.windows.net/mass/codes_en"
fi

# download gigaword
if [ ! -e "./$rocs" ]; then
    echo "== Download ROC Stories =="
    mkdir ROCStories
    wget https://goo.gl/0OYkPK -O $rocs/$rocs-2017.csv
    wget https://goo.gl/7R59b1 -O $rocs/$rocs-2016.csv
    python preprocess_rocstories.py --dirpath $rocs
fi

# process roc stories
echo "== Process ROC Stories =="
bash get-data-rocstories.sh \
     --replace_ner true \
     --replace_unk true \
     --reload_vocab vocab_en \
     --reload_codes codes_en \
     --rocspath $rocs

# download pre-trained model
if [ ! -e "./mass_summarization_1024.pth" ]; then
    echo "== Download pre-trained model =="
    wget "https://modelrelease.blob.core.windows.net/mass/mass_summarization_1024.pth"
fi