import pickle
import os
import json
from typing import List, Dict, Tuple, Union
from gensim.models import KeyedVectors

from .config import Config
from .misc import print_header, download_file


class Model:
    """ A simple abstraction layer for using the Word Embedding Model """

    def __init__(self, load_model: bool = True, use_full_model: bool = False, silent: bool = False):
        """Initialises the Model class.

        Args:
            load_model (bool, optional): If True, loads the models during initialization. Defaults to True.
            use_full_model (bool, optional): If True, loads the full Word2Vec model. Defaults to False.
            silent (bool, optional): If True, suppresses print statements. Defaults to False.
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

# =============================================================================
#     LOADER
# =============================================================================

    def load_models(self) -> None:
        """Loads the necessary models based on configuration.

        Always loads the cached model. If `use_full_model` is True, also loads the full Word2Vec model.
        """
        self.__load_cached_model()
        if self.use_full_model:
            self.__load_word2vec_model()

# =============================================================================
#     CACHED MODEL
# =============================================================================

    def __ensure_cached_model(self) -> None:
        """Ensures the cached model file exists locally.

        Checks if the cached model file exists at the configured path.
        If not, it downloads the file from the remote URL.
        """
        local_path = self.config.get_cached_model()
        if not os.path.exists(local_path):
            if not self.silent:
                print('Beginning download of cached model from', self.config.get_cahed_model_remote_url())
            download_file(self.config.get_cahed_model_remote_url(), local_path)

    def __load_cached_model(self) -> None:
        """Loads the cached token-to-CSO mapping from the JSON file.

        This method ensures the file exists before attempting to load it.
        The loaded data is stored in `self.model`.
        """
        self.__ensure_cached_model()
        with open(self.config.get_cached_model(), "r", encoding="utf-8") as file:
            self.model = json.load(file)
        if not self.silent:
            print("Cached model loaded.")

    def check_word_in_model(self, word: str) -> bool:
        """Checks if a word exists in the cached model.

        Args:
            word (str): The word to check.

        Returns:
            bool: True if the word is in the cached model, False otherwise.
        """
        return word in self.model

    def get_words_from_model(self, word: str) -> List[Dict]:
        """Retrieves CSO topics associated with a word from the cached model.

        Args:
            word (str): The word to look up.

        Returns:
            List[Dict]: A list of dictionaries containing topic information, or an empty list if not found.
        """
        return self.model.get(word, {})



# =============================================================================
#     FULL MODEL
# =============================================================================


    def __ensure_word2vec_model(self) -> None:
        """Ensures the full Word2Vec model file exists locally.

        Checks if the model file exists at the configured path.
        If not, it downloads the file from the remote URL.
        """
        local_path = self.config.get_model_pickle_path()
        if not os.path.exists(local_path):
            if not self.silent:
                print('Beginning model download from', self.config.get_model_pickle_remote_url())
            download_file(self.config.get_model_pickle_remote_url(), local_path)

    def __load_word2vec_model(self) -> None:
        """Loads the full Word2Vec model into memory.

        Uses Gensim's KeyedVectors to load the model. Sets `self.embedding_size` based on the loaded model.
        """
        self.__ensure_word2vec_model()
        path = self.config.get_model_pickle_path()


        try:
            with open(path, "rb") as fh:
                model_kv = pickle.load(fh)
            if hasattr(model_kv, "key_to_index"):  # KeyedVectors in Gensim 4
                self.full_model = model_kv
                self.embedding_size = int(self.full_model.vector_size)
            else:
                raise TypeError("Unsupported pickle contents for word2vec model.")
            if not self.silent:
                print("Word2Vec model loaded.")
        except Exception as e_pk:
            raise RuntimeError(
                f"Failed to load word2vec model from '{path}'.\n"
                f"- Pickle fallback error: {e_pk}"
            )




    def check_word_in_full_model(self, word: str) -> bool:
        """Checks if a word exists in the full Word2Vec model vocabulary.

        Args:
            word (str): The word to check.

        Returns:
            bool: True if the word is in the vocabulary, False otherwise.

        Raises:
            ValueError: If the full model is not loaded.
        """
        if not self.use_full_model:
            raise ValueError('The full word2vec model is not loaded. Set fast_classification = False')
        if self.full_model is None:
            raise ValueError('The full word2vec model is not loaded. Set fast_classification = False')
        if word in self.full_model.key_to_index:  # Gensim 4 vocab
            return True
        else:
            return False


    def get_embedding_from_full_model(self, word: str) -> List[float]:
        """Retrieves the embedding vector for a given word.

        Args:
            word (str): The word to look up.

        Returns:
            List[float]: The embedding vector as a list of floats. Returns a zero vector if the word is missing.

        Raises:
            ValueError: If the full model is not loaded.
        """
        if not self.use_full_model:
            raise ValueError('The full word2vec model is not loaded. Set fast_classification = False')
        if self.full_model is None:
            return [0] * self.embedding_size
        try:
            vec = self.full_model[word]  # KeyedVectors supports __getitem__
            return vec.tolist()
        except KeyError:
            return [0] * self.embedding_size
        

    def get_top_similar_words_from_full_model(self, grams: Union[str, List[str]]) -> List[Tuple[str, float]]:
        """Finds the top similar words to the given input from the full model.

        Args:
            grams (Union[str, List[str]]): A single word or a list of words to find similarities for.

        Returns:
            List[Tuple[str, float]]: A list of tuples (word, similarity_score) for words exceeding the similarity threshold.

        Raises:
            ValueError: If the full model is not loaded.
        """
        if not self.use_full_model:
            raise ValueError('The full word2vec model is not loaded. Set fast_classification = False')
        if self.full_model is None:
            return []
        try:
            sims = self.full_model.most_similar(grams, topn=self.top_amount_of_words)
            return [(token, score) for (token, score) in sims if score >= self.word_similarity]
        except KeyError:
            return []


    def get_embedding_size(self) -> int:
        """Returns the size of the embedding vectors.

        Returns:
            int: The size of the embedding vectors.

        Raises:
            ValueError: If the full model is not loaded.
        """
        if not self.use_full_model:
            raise ValueError('The full word2vec model is not loaded. Set fast_classification = False')
        return int(self.embedding_size)


# =============================================================================
#     SETUP - UPDATE HELPERS
# =============================================================================

    @staticmethod
    def setup() -> None:
        """Sets up the necessary model files.

        Downloads the cached model and the full Word2Vec model if they are missing locally.
        """
        config = Config()
        print_header("MODELS: CACHED & WORD2VEC")

        # Cached JSON
        if not os.path.exists(config.get_cached_model()):
            print('Beginning download of cached model from', config.get_cahed_model_remote_url())
            task_completed = download_file(config.get_cahed_model_remote_url(), config.get_cached_model())
            print("Cached model downloaded successfully." if task_completed else "Failed to download cached model.")
        else:
            print("Nothing to do. The cached model is already available.")

        # Full model (may be .bin or pickle)
        if not os.path.exists(config.get_model_pickle_path()):
            print('Beginning download of word2vec model from', config.get_model_pickle_remote_url())
            task_completed = download_file(config.get_model_pickle_remote_url(), config.get_model_pickle_path())
            print("Word2Vec model downloaded successfully." if task_completed else "Failed to download word2vec model.")
        else:
            print("Nothing to do. The word2vec model is already available.")

    @staticmethod
    def update() -> None:
        """Updates the model files by forcing a re-download.

        Deletes existing local model files and downloads the latest versions from the remote URLs.
        """
        config = Config()
        print_header("MODELS: CACHED & WORD2VEC")
        try:
            os.remove(config.get_cached_model())
        except FileNotFoundError:
            print("Couldn't delete cached model: not found")

        try:
            os.remove(config.get_model_pickle_path())
        except FileNotFoundError:
            print("Couldn't delete word2vec model: not found")

        print("Updating the models: cached and word2vec")
        task_completed1 = download_file(config.get_cahed_model_remote_url(), config.get_cached_model())
        task_completed2 = download_file(config.get_model_pickle_remote_url(), config.get_model_pickle_path())
        if task_completed1 and task_completed2:
            print("Models downloaded successfully.")