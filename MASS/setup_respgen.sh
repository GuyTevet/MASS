cmdc=cmdc # the path of your roc stories dataset

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

# download Cornell Movie Dialog Corpus
if [ ! -e "./$cmdc" ]; then
    echo "== Download Cornell Movie Dialog Corpus =="
    mkdir $cmdc
    wget -c 'https://www.dropbox.com/s/ncfa5t950gvtaeb/test.enc?dl=0' -O $cmdc/test.enc.txt
    wget -c 'https://www.dropbox.com/s/48ro4759jaikque/test.dec?dl=0' -O $cmdc/test.dec.txt
    wget -c 'https://www.dropbox.com/s/gu54ngk3xpwite4/train.enc?dl=0' -O $cmdc/train.enc.txt
    wget -c 'https://www.dropbox.com/s/g3z2msjziqocndl/train.dec?dl=0' -O $cmdc/train.dec.txt
fi

# process roc stories
echo "== Process Cornell Movie Dialog Corpus =="
bash get-data-cmdc.sh \
     --replace_ner true \
     --replace_unk true \
     --reload_vocab vocab_en \
     --reload_codes codes_en \
     --cmdcpath $cmdc

# download pre-trained model
if [ ! -e "./mass_summarization_1024.pth" ]; then
    echo "== Download pre-trained model =="
    wget "https://modelrelease.blob.core.windows.net/mass/mass_summarization_1024.pth"
fi