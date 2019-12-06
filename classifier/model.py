import pickle
import os
import sys
import requests
from hurry.filesize import size
import json


#some global variables
dir = os.path.dirname(os.path.realpath(__file__))
MODEL_PICKLE_PATH = f"{dir}/models/model.p"
MODEL_PICKLE_REMOTE_URL = "https://cso.kmi.open.ac.uk/download/model.p"
CACHED_MODEL = f"{dir}/models/token-to-cso-combined.json"
CACHED_MODEL_REMOTE_URL = "https://cso.kmi.open.ac.uk/download/token-to-cso-combined.json"


class Model:
    """ A simple abstraction layer for using the Word Embedding Model """
    
    def __init__(self):
        """ Initialising the model class
        """
        self.model = dict()
        self.load_chached_model()
        
    def check_word_in_model(self, word):
        
        if word in self.model:
            return True
        
        return False

    def get_words_from_model(self, word):
        try:
            return self.model[word]
        except KeyError:
            return {}

    def load_chached_model(self):
        """Function that loads both CSO and the cached Word2vec model. 
        The ontology file has been serialised with Pickle. 
        The cached model is a json file (dictionary) containing all words in the corpus vocabulary with the corresponding CSO topics.
        The latter has been created to speed up the process of retrieving CSO topics given a token in the metadata
        
    
        Args:
    
        Returns:
            fcso (dictionary): contains the CSO Ontology.
            fmodel (dictionary): contains a cache of the model, i.e., each token is linked to the corresponding CSO topic.
        """
        
        self.check_cached_model()
        with open(CACHED_MODEL) as f:
           self.model = json.load(f)
        

     

    def check_cached_model(self):
        """Function that checks if the cached model is available. If not, it will attempt to download it from a remote location.
        Tipically hosted on the CSO Portal.
    
        """
        
        if not os.path.exists(CACHED_MODEL):
            print('[*] Beginning download of cached model from', CACHED_MODEL_REMOTE_URL)
            self.download_file(CACHED_MODEL_REMOTE_URL, CACHED_MODEL)
        
        
    def download_file(self, url, filename):
        """Function that downloads the model from the web.
    
        Args:
            url (string): Url of where the model is located.
            filename (string): location of where to save the model
    
        Returns:
            
        """
        with open(filename, 'wb') as f:
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
                    f.write(data)
                    done = int(50*downloaded/total)
                    sys.stdout.write('\r[{}{}] {}/{}'.format('█' * done, '.' * (50-done), size(downloaded), size(total)))
                    sys.stdout.flush()
                sys.stdout.write('\n')
                print('[*] Done!')
                
            
            
            
    ###########################################################
    #########
    ######### 
    #########  LEGACY CODE: just in case we want to use 
    #########   the model as is
    #########
    ###########################################################
            
    def load_model(self):
        """Function that loads both CSO and Word2vec model. 
        This file has been serialised using Pickle allowing to be loaded quickly.
        
    
        Args:
    
        Returns:
            fmodel (dictionary): contains the word2vec model.
        """
        
        self.check_model()
        self.model = pickle.load(open(MODEL_PICKLE_PATH, "rb"))
    
                
    def check_model(self):
        """Function that checks if the model is available. If not, it will attempt to download it from a remote location.
        Tipically hosted on the CSO Portal.
    
        """
        
        if not os.path.exists(MODEL_PICKLE_PATH):
            print('[*] Beginning model download from', MODEL_PICKLE_REMOTE_URL)
            self.download_file(MODEL_PICKLE_REMOTE_URL, MODEL_PICKLE_PATH)  







