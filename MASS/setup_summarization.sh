# install tools
bash install-tools.sh

# download vocab + codes
wget "https://modelrelease.blob.core.windows.net/mass/vocab_en"
wget "https://modelrelease.blob.core.windows.net/mass/codes_en"

# download gigaword
# wget "https://drive.google.com/uc?export=download&confirm=iKZV&id=0B6N7tANPyVeBNmlSX19Ld2xDU1E"
python download_gigaword.py

# process gigaword
gigaword=sumdata # the path of your gigaword dataset 
bash get-data-gigaword.sh \
     --replace_ner true \
     --replace_unk true \
     --reload_vocab vocab_en \
     --reload_codes codes_en \
     --gigapath $gigaword

# download pre-trained model
wget "https://modelrelease.blob.core.windows.net/mass/mass_summarization_1024.pth"
