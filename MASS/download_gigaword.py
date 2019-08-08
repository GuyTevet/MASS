import requests
import os
import tarfile


def download_file_from_google_drive(id, destination):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination)

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

def untar(src):
    with tarfile.open(src) as tar:
        tar.extractall()


if __name__ == "__main__":
    file_id = '0B6N7tANPyVeBNmlSX19Ld2xDU1E'
    destination = os.path.join(os.getcwd(), 'gigaword.tar')
    if not os.path.exists(destination):
        print('Download data to [{}]'.format(destination))
        download_file_from_google_drive(file_id, destination)
    untar(destination)