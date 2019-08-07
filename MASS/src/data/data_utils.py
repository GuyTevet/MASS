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

def download_files(url, file_list, target_dir):

    import urllib

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    for file in file_list:
        target_path = os.path.join(target_dir,file)
        if not os.path.exists(target_path):
            print('downloading [{}]...'.format(file))
            urllib.request.urlretrieve(url + file, target_path)

def untar(src):
    with tarfile.open(src) as tar:
        tar.extractall()


if __name__ == "__main__":
    data_path = os.getcwd()
    file_id = '0B6N7tANPyVeBNmlSX19Ld2xDU1E'
    destination = os.path.join(data_path, 'gigaword.tar')
    if not os.path.isdir(data_path):
        os.makedirs(data_path)
    if not os.path.exists(destination):
        print('Download data to [{}]'.format(destination))
        download_file_from_google_drive(file_id, destination)
    untar(destination)