import sys
from typing import Dict, Iterator
from itertools import islice
import os
from hurry.filesize import size
import requests

def download_file(url: str, filename: str) -> bool:
    """Downloads a file from a given URL with a progress bar.

    This function handles the creation of the parent directory if it does not exist.
    It streams the download and displays a progress bar in the console. If the
    download fails or is interrupted, it attempts to clean up the partial file.

    Args:
        url (str): The source URL to download from.
        filename (str): The local file path where the file will be saved.

    Returns:
        bool: True if the file was successfully downloaded, False otherwise.
    """
    try:
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)

        with requests.get(url, stream=True, timeout=30) as response:
            response.raise_for_status()
            total = response.headers.get('content-length')

            if total is None:
                print('There was an error while downloading: missing content-length header.')
                return False

            total = int(total)
            downloaded = 0
            with open(filename, 'wb') as file:
                for data in response.iter_content(chunk_size=max(int(total / 1000), 1024 * 1024)):
                    if not data:
                        continue
                    downloaded += len(data)
                    file.write(data)
                    done = int(50 * downloaded / total)
                    sys.stdout.write('\r[{}{}] {}/{}'.format('█' * done, '.' * (50 - done), size(downloaded), size(total)))
                    sys.stdout.flush()
            sys.stdout.write('\n')
            print('[*] Done!')
            return True
    except requests.RequestException as e:
        sys.stdout.write('\n')
        print(f"Download failed: {e}")
        # Clean up partial file
        try:
            if os.path.exists(filename):
                os.remove(filename)
        except Exception:
            pass
        return False
    

def chunks(data: Dict, size: int) -> Iterator[Dict]:
    """Splits a dictionary into smaller dictionaries of a specified size.

    This function yields successive n-sized chunks from the input dictionary.
    It is useful for processing large dictionaries in batches.

    Args:
        data (Dict): The dictionary to split.
        size (int): The maximum size of each chunk.

    Yields:
        Iterator[Dict]: An iterator yielding dictionaries of size `size` (or smaller for the last chunk).
    """
    # https://stackoverflow.com/questions/22878743/how-to-split-dictionary-into-multiple-dictionaries-fast
    iterator = iter(data)
    for _ in range(0, len(data), size):
        yield {k:data[k] for k in islice(iterator, size)}


def download_language_model(notification: bool = True) -> None:
    """Downloads and ensures necessary NLP language resources are installed.

    This function checks for the presence of the spaCy 'en_core_web_sm' model
    and NLTK resources ('punkt' and 'stopwords'). If they are missing, it
    attempts to download them.

    Args:
        notification (bool, optional): If True, prints status messages to stdout.
            Defaults to True.

    Raises:
        Exception: If downloading the spaCy model or NLTK resources fails.
    """
    import nltk
    import spacy

    if notification:
        print_header("LANGUAGE MODEL")

    # --- spaCy model ---
    if notification:
        print("Checking spaCy model: en_core_web_sm")
    try:
        spacy.load("en_core_web_sm")
        if notification:
            print("spaCy model already present.")
    except OSError:
        if notification:
            print("spaCy model not found. Downloading 'en_core_web_sm' ...")
        try:
            from spacy.cli import download as spacy_download
            spacy_download("en_core_web_sm")
            # Verify load
            spacy.load("en_core_web_sm")
            if notification:
                print("spaCy model installed successfully.")
        except Exception as e:
            print(f"Failed to download spaCy model: {e}")
            raise

    # --- NLTK resources ---
    if notification:
        print("Ensuring NLTK resources: punkt, stopwords")
    try:
        # Idempotent: will no-op if already present
        nltk.download("punkt", quiet=True)
        nltk.download("stopwords", quiet=True)
        if notification:
            print("NLTK resources are ready.")
    except Exception as e:
        print(f"Failed to download NLTK resources: {e}")
        raise


def download_croissant_specification(notification: bool = True, force: bool = False) -> None:
    """Downloads the Croissant base specification file.

    This function checks if the Croissant base specification file exists locally.
    If it is missing or if `force` is set to True, it downloads the file from
    the remote URL specified in the configuration.

    Args:
        notification (bool, optional): If True, prints status messages to stdout.
            Defaults to True.
        force (bool, optional): If True, forces the download even if the file
            already exists locally. Defaults to False.
    """
    from .config import Config
    config = Config()
    if notification:
        print_header("CROISSANT SPECIFICATION")

    local_path = config.get_croissant_base_specification_path()
    if not os.path.exists(local_path) or force:
        if notification:
            print('[*] Beginning download of cached model from', config.get_croissant_base_specification_remote_path())
        download_file(config.get_croissant_base_specification_remote_path(), local_path)
    else:
        print(f"File {local_path} alredy exists.")


def print_header(header: str) -> None:
    """Prints a formatted header to the console.

    Used for displaying setup, update, or version messages in a consistent format.

    Args:
        header (str): The text to display inside the header box.
    """
    print()
    print("# ======================================================")
    print(f"#     {header}")
    print("# ======================================================")