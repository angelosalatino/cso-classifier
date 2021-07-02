import sys
from itertools import islice
import os
from hurry.filesize import size
import requests


def download_file(url, filename):
    """Function that downloads the model from the web.

    Args:
        url (string): Url of where the model is located.
        filename (string): location of where to save the model

    Returns:
        boolean: whether it is successful or not.
    """
    is_downloaded = False
    with open(filename, 'wb') as file:
        response = requests.get(url, stream=True)
        total = response.headers.get('content-length')

        if total is None:
            #f.write(response.content)
            print('There was an error while downloading the new version of the ontology.')
        else:
            downloaded = 0
            total = int(total)
            for data in response.iter_content(chunk_size=max(int(total/1000), 1024*1024)):
                downloaded += len(data)
                file.write(data)
                done = int(50*downloaded/total)
                sys.stdout.write('\r[{}{}] {}/{}'.format('█' * done, '.' * (50-done), size(downloaded), size(total)))
                sys.stdout.flush()
            sys.stdout.write('\n')
            print('[*] Done!')
            is_downloaded = True

    return is_downloaded


def chunks(data, size):
    """Yield successive n-sized chunks from l.
    """
    # https://stackoverflow.com/questions/22878743/how-to-split-dictionary-into-multiple-dictionaries-fast
    iterator = iter(data)
    for i in range(0, len(data), size):
        yield {k:data[k] for k in islice(iterator, size)}


def download_language_model(notification = True):
    """ Function for downloading the language model.
    """
    if notification:
        print_header("LANGUAGE MODEL")
        print("Downloading and setting up spaCy language model ")

    os.system("python -m spacy download en_core_web_sm")
    
    if notification:
        print("Downloading and setting up NLTK stopwords")
    import nltk
    nltk.download('stopwords')


def print_header(header):
    """ Printing header. Used when setting up, updating, versioning and so on.
    """
    print()
    print("# ======================================================")
    print("#     {}".format(header))
    print("# ======================================================")