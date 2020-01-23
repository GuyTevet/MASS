reddit=reddit_dialog # the path of your roc stories dataset

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

# assert data exists
if [ ! -e "./$reddit" ]; then
    echo "Error: You should first download the data manually from Dropbox and put it in [$reddit] dir!"
fi

# process roc stories
echo "== Process Reddit dialog =="
bash get-data-reddit.sh \
     --replace_ner true \
     --replace_unk true \
     --reload_vocab vocab_en \
     --reload_codes codes_en \
     --rocspath $reddit

# download pre-trained model
if [ ! -e "./mass_summarization_1024.pth" ]; then
    echo "== Download pre-trained model =="
    wget "https://modelrelease.blob.core.windows.net/mass/mass_summarization_1024.pth"
fi