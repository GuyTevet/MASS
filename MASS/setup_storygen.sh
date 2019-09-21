# install tools
if [ ! -e "./tools" ]; then
    echo "== Installing Tools =="
    bash install-tools.sh
fi

# download vocab + codes
if [ ! -e "./tools" ]; then
    echo "== Download vocab + codes =="
    wget "https://modelrelease.blob.core.windows.net/mass/vocab_en"
    wget "https://modelrelease.blob.core.windows.net/mass/codes_en"
fi

# download gigaword
if [ ! -e "./ROCStories" ]; then
    echo "== Download ROC Stories =="
    mkdir ROCStories
    wget https://goo.gl/0OYkPK -O ROCStories/ROCStories-2017.csv
    wget https://goo.gl/7R59b1 -O ROCStories/ROCStories-2016.csv
fi

# process gigaword
# TBD

# download pre-trained model
if [ ! -e "./mass_summarization_1024.pth" ]; then
    echo "== Download pre-trained model =="
    wget "https://modelrelease.blob.core.windows.net/mass/mass_summarization_1024.pth"
fi