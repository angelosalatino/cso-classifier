import pickle
import os
import json

from classifier.config import Config
from classifier import misc


class Model:
    """ A simple abstraction layer for using the Word Embedding Model """
    
    def __init__(self, load_model = True):
        """ Initialising the model class
        """
        self.model = dict()
        self.config = Config()
        if load_model:
            self.load_chached_model()

        
    def check_word_in_model(self, word):
        """ It checks whether a word is available in the model
        """
        if word in self.model:
            return True
        
        return False


    def get_words_from_model(self, word):
        """ Returns the similar words to the word:word
        Args:
            word (string): word that potentially belongs to the model
        
        Return:
            dictionary: containing info about the most similar words to word. Empty if the word is not in the model.
        """
        try:
            return self.model[word]
        except KeyError:
            return {}


    def load_chached_model(self):
        """Function that loads the cached Word2vec model. 
        The ontology file has been serialised with Pickle. 
        The cached model is a json file (dictionary) containing all words in the corpus vocabulary with the corresponding CSO topics.
        The latter has been created to speed up the process of retrieving CSO topics given a token in the metadata
        """
        
        self.check_cached_model()
        with open(self.config.get_cached_model()) as f:
           self.model = json.load(f)
        print("Model loaded.")
           
    
    def check_cached_model(self, notification = False):
        """Function that checks if the cached model is available. If not, it will attempt to download it from a remote location.
        Tipically hosted on the CSO Portal.
        """
        if not os.path.exists(self.config.get_cached_model()):
            print('[*] Beginning download of cached model from', self.config.get_cahed_model_remote_url())
            misc.download_file(self.config.get_cahed_model_remote_url(), self.config.get_cached_model())

  
    def setup(self):
        """Function that sets up the word2vec model
        """
        misc.print_header("CACHED WORD2VEC MODEL")
        
        if not os.path.exists(self.config.get_cached_model()):
            print('[*] Beginning download of cached model from', self.config.get_cahed_model_remote_url())
            task_completed = misc.download_file(self.config.get_cahed_model_remote_url(), self.config.get_cached_model())

            if task_completed:
                print("File containing the model has been downloaded successfully.")
            else:
                print("We were unable to complete the download of the model.")
        else:
            print("Nothing to do. The model is already available.")
    

    def update(self, force = False): 
        """Function that updates the model
        The variable force is for the future when we will have model versioning.
        """
        misc.print_header("CACHED WORD2VEC MODEL")
        try:
            os.remove(self.config.get_cached_model())
        except FileNotFoundError:
            print("The file model not found")
        print("Updating the cached word2vec model")
        misc.download_file(self.config.get_cahed_model_remote_url(), self.config.get_cached_model())


      
# =============================================================================
#         LEGACY CODE: just in case we want to use the model as is
# =============================================================================
            
    def load_model(self):
        """Function that loads Word2vec model. 
        This file has been serialised using Pickle allowing to be loaded quickly.
        """
        self.check_model()
        self.model = pickle.load(open(self.config.get_model_pickle_path(), "rb"))
    
                
    def check_model(self):
        """Function that checks if the model is available. If not, it will attempt to download it from a remote location.
        Tipically hosted on the CSO Portal.
        """
        if not os.path.exists(self.config.get_model_pickle_path()):
            print('[*] Beginning model download from', self.config.get_model_pickle_remote_url())
            misc.download_file(self.config.get_model_pickle_remote_url(), self.config.get_model_pickle_path())  







