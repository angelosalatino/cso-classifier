import sys
import requests
from hurry.filesize import size
from itertools import islice
import os


def download_file(url, filename):
    """Function that downloads the model from the web.

    Args:
        url (string): Url of where the model is located.
        filename (string): location of where to save the model

    Returns:
        boolean: whether it is successful or not.
    """
    with open(filename, 'wb') as f:
        response = requests.get(url, stream=True)
        total = response.headers.get('content-length')

        if total is None:
            #f.write(response.content)
            print('There was an error while downloading the new version of the ontology.')
            return False
        else:
            downloaded = 0
            total = int(total)
            for data in response.iter_content(chunk_size=max(int(total/1000), 1024*1024)):
                downloaded += len(data)
                f.write(data)
                done = int(50*downloaded/total)
                sys.stdout.write('\r[{}{}] {}/{}'.format('█' * done, '.' * (50-done), size(downloaded), size(total)))
                sys.stdout.flush()
            sys.stdout.write('\n')
            print('[*] Done!')
            return True
    
    return False


def chunks(data, size):
    """Yield successive n-sized chunks from l.
    """
    # https://stackoverflow.com/questions/22878743/how-to-split-dictionary-into-multiple-dictionaries-fast
    it = iter(data)
    for i in range(0, len(data), size):
        yield {k:data[k] for k in islice(it, size)}
        
        
def download_language_model(notification = True):
    """ Function for downloading the language model.
    """
    if notification:
        print_header("LANGUAGE MODEL")
              
    os.system("python -m spacy download en_core_web_sm")
    
    
def print_header(header):
    """ Printing header. Used when setting up, updating, versioning and so on.
    """
    print()
    print("# ==============================")
    print("#     {}".format(header))
    print("# ==============================")