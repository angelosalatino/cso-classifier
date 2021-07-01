import pickle
import os
import json

from .config import Config
from .misc import print_header, download_file


class Model:
    """ A simple abstraction layer for using the Word Embedding Model """

    def __init__(self, load_model = True, use_full_model = False, silent = False):
        """ Initialising the model class
        """
        self.silent = silent
        self.model = dict()
        self.full_model = None
        self.config = Config()

        self.embedding_size = 0
        self.word_similarity = 0.7# similarity of words in the model
        self.top_amount_of_words = 10 # maximum number of words to select

        self.use_full_model = use_full_model

        if load_model:
            self.load_models()


    def load_models(self):
        """Function that loads both models.
        """
        self.__load_chached_model()
        if self.use_full_model:
            self.__load_word2vec_model()

# =============================================================================
#     CACHED MODEL
# =============================================================================

    def check_word_in_model(self, word):
        """ It checks whether a word is available in the cached model
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


    def __check_cached_model(self):
        """Function that checks if the cached model is available. If not, it will attempt to download it from a remote location.
        Tipically hosted on the CSO Portal.
        """
        if not os.path.exists(self.config.get_cached_model()):
            print('[*] Beginning download of cached model from', self.config.get_cahed_model_remote_url())
            download_file(self.config.get_cahed_model_remote_url(), self.config.get_cached_model())


    def __load_chached_model(self):
        """Function that loads the cached Word2vec model.
        The ontology file has been serialised with Pickle.
        The cached model is a json file (dictionary) containing all words in the corpus vocabulary with the corresponding CSO topics.
        The latter has been created to speed up the process of retrieving CSO topics given a token in the metadata
        """

        self.__check_cached_model()
        with open(self.config.get_cached_model()) as file:
            self.model = json.load(file)
        if not self.silent:
            print("Model loaded.")



# =============================================================================
#     FULL MODEL
# =============================================================================

    def check_word_in_full_model(self, word):
        """ It checks whether a word is available in the word2vec model
        """
        if self.use_full_model:
            if word in self.full_model:
                return True

            return False

        raise ValueError('The full word2vec model is not loaded. Make sure you set fast_classification = False')

    def get_embedding_from_full_model(self, word):
        """ Returns the embedding vector of the word:word
        Args:
            word (string): word that potentially belongs to the model

        Return:
            list (of size self.embedding_size): containing all embedding values
        """
        if self.use_full_model:
            try:
                return self.full_model[word]
            except KeyError:
                return [0]*self.embedding_size #array full of zeros: just don't move in the embedding space
        else:
            raise ValueError('The full word2vec model is not loaded. Make sure you set fast_classification = False')


    def get_top_similar_words_from_full_model(self, grams):
        """Function that identifies the top similar words in the model that have similarity higher than th.

        Args:
            list_of_words (list of tuples): It contains the topics found with string similarity.
            th (integer): threshold

        Returns:
            result (dictionary): containing the found topics with their similarity and the n-gram analysed.
        """
        if self.use_full_model:
            result = list()
            try:
                list_of_words = self.full_model.most_similar(grams, topn=self.top_amount_of_words)
                #result = [y for (x,y) in enumerate(list_of_words) if y[1] >= th]
                result = [(x,y) for (x,y) in list_of_words if y >= self.word_similarity]
            except KeyError:
                pass
            return result

        raise ValueError('The full word2vec model is not loaded. Make sure you set fast_classification = False')


    def get_embedding_size(self):
        """Function that returns the size of the embedding model.
        """
        if self.use_full_model:
            return self.embedding_size

        raise ValueError('The full word2vec model is not loaded. Make sure you set fast_classification = False')


    def __check_word2vec_model(self):
        """Function that checks if the model is available. If not, it will attempt to download it from a remote location.
        Tipically hosted on the CSO Portal.
        """
        if not os.path.exists(self.config.get_model_pickle_path()):
            print('[*] Beginning model download from', self.config.get_model_pickle_remote_url())
            download_file(self.config.get_model_pickle_remote_url(), self.config.get_model_pickle_path())


    def __load_word2vec_model(self):
        """Function that loads Word2vec model.
        This file has been serialised using Pickle allowing to be loaded quickly.
        """
        self.__check_word2vec_model()
        self.full_model = pickle.load(open(self.config.get_model_pickle_path(), "rb"))
        self.embedding_size = self.full_model.vector_size


# =============================================================================
#     CONFIG
# =============================================================================

    @staticmethod
    def setup():
        """Function that sets up the word2vec model
        """
        config = Config()
        print_header("MODELS: CACHED & WORD2VEC")
        if not os.path.exists(config.get_cached_model()):
            print('[*] Beginning download of cached model from', config.get_cahed_model_remote_url())
            task_completed = download_file(config.get_cahed_model_remote_url(), config.get_cached_model())

            if task_completed:
                print("File containing the cached model has been downloaded successfully.")
            else:
                print("We were unable to complete the download of the cached model.")
        else:
            print("Nothing to do. The cached model is already available.")

        if not os.path.exists(config.get_model_pickle_path()):
            print('[*] Beginning download of word2vec model from', config.get_model_pickle_remote_url())
            task_completed = download_file(config.get_model_pickle_remote_url(), config.get_model_pickle_path())

            if task_completed:
                print("File containing the word2vec model has been downloaded successfully.")
            else:
                print("We were unable to complete the download of the word2vec model.")
        else:
            print("Nothing to do. The word2vec model is already available.")


    @staticmethod
    def update():
        """Function that updates the models
        The variable force is for the future when we will have models versioning.
        """
        config = Config()
        print_header("MODELS: CACHED & WORD2VEC")
        try:
            os.remove(config.get_cached_model())
        except FileNotFoundError:
            print("Couldn't delete file cached model: not found")

        try:
            os.remove(config.get_model_pickle_path())
        except FileNotFoundError:
            print("Couldn't delete file word2vec model: not found")
        print("Updating the models: cached and word2vec")
        task_completed1 = download_file(config.get_cahed_model_remote_url(), config.get_cached_model())
        task_completed2 = download_file(config.get_model_pickle_remote_url(), config.get_model_pickle_path())
        if task_completed1 and task_completed2:
            print("Models downloaded successfully.")
