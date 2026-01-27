import warnings
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from kneed import KneeLocator
from rapidfuzz.distance import Levenshtein
from nltk import everygrams

from .model import Model
from .ontology import Ontology
from .paper import Paper

class Semantic:
    """ A simple abstraction layer for using the Semantic module of the CSO classifier """

    def __init__(self, model: Optional[Model] = None, cso: Optional[Ontology] = None, fast_classification: bool = True, paper: Optional[Paper] = None):
        """Function that initialises an object of class CSOClassifierSemantic and all its members.

        Args:
            model (Optional[Model], optional): word2vec model. Defaults to None.
            cso (Optional[Ontology], optional): Computer Science Ontology. Defaults to None.
            fast_classification (bool, optional): Determines if the cached model should be used. Defaults to True.
            paper (Optional[Paper], optional): The paper object. Defaults to None.
        """
        self.cso = cso                  #Stores the CSO Ontology
        self.paper = paper              #Paper to analyse
        self.model = model              #contains the cached model
        self.min_similarity = 0.90      #Initialises the min_similarity
        self.fast_classification = fast_classification # if will use the full model or not
        self.explanation = dict()
        self.extracted_topics = dict()  # dictionary with the extract topics (including similarity measures)


    def set_paper(self, paper: Paper) -> None:
        """Function that initializes the paper variable in the class.

        Args:
            paper (Paper): The paper to analyse.
        """
        self.paper = paper
        self.reset_explanation()


    def set_min_similarity(self, min_similarity: float) -> None:
        """Function that initializes the minimum similarity variable.

        Args:
            min_similarity (float): value of min_similarity between 0 and 1.
        """
        self.min_similarity = min_similarity


    def reset_explanation(self) -> None:
        """ Resetting the explanation
        """
        self.explanation = dict()


    def get_explanation(self) -> Dict[str, Set[str]]:
        """ Returns the explanation

        Returns:
            Dict[str, Set[str]]: The explanation dictionary.
        """
        return self.explanation


    def classify_semantic(self) -> List[str]:
        """Function that classifies the paper on a semantic level. This semantic module follows four steps:
            (i) entity extraction,
            (ii) CSO concept identification,
            (iii) concept ranking, and
            (iv) concept selection.

        Returns:
            List[str]: list of identified topics.
        """

        ##################### Core analysis
        found_topics, explanation = self.__find_topics(self.paper.get_semantic_chunks())

        ##################### Ranking
        self.extracted_topics = self.__rank_topics(found_topics, explanation)

        final_topics = list(self.extracted_topics.keys())

        return final_topics

    def get_semantic_topics_weights(self) -> Dict[str, float]:
        """Function that returns the full set of topics with the similarity measure

        Returns:
            Dict[str, float]: containing the found topics with their metric.
        """
        return self.extracted_topics #they are already in the correct format.


    def __find_topics(self, concepts: List[str]) -> Tuple[Dict[str, Any], Dict[str, Set[str]]]:
        """Function that identifies topics starting from the ngram forund in the paper

        Args:
            concepts (List[str]): Chunks of text to analyse.

        Returns:
            Tuple[Dict[str, Any], Dict[str, Set[str]]]: A tuple containing the identified topics and the explanation.
        """

        # Set up
        found_topics = dict() # to store the matched topics
        explanation = dict()

        # finding matches
        for concept in concepts:
            evgrams = everygrams(concept.split(), 1, 3) # list of unigrams, bigrams, trigrams
            for grams in evgrams:
                gram = "_".join(grams)
                gram_without_underscore = " ".join(grams)
                #### Finding similar words contained in the model

                list_of_matched_topics = []

                if self.fast_classification:
                    list_of_matched_topics = self.__get_similar_words_from_cached_model(gram,grams)
                else:
                    list_of_matched_topics = self.__get_similar_words_from_full_model(gram, grams)


                for topic_item in list_of_matched_topics:

                    topic   = topic_item["topic"]
                    str_sim = topic_item["sim_t"]
                    wet     = topic_item["wet"]
                    sim     = topic_item["sim_w"]


                    if str_sim >= self.min_similarity and topic in self.cso.topics_wu:


                        if topic in found_topics:
                            #tracking this match
                            found_topics[topic]["times"] += 1

                            found_topics[topic]["gram_similarity"].append(sim)

                            #tracking the matched gram
                            if gram in found_topics[topic]["grams"]:
                                found_topics[topic]["grams"][gram] += 1
                            else:
                                found_topics[topic]["grams"][gram] = 1

                            #tracking the most similar gram to the topic
                            if str_sim > found_topics[topic]["embedding_similarity"]:
                                found_topics[topic]["embedding_similarity"] = str_sim
                                found_topics[topic]["embedding_matched"] = wet

                        else:
                            #creating new topic in the result set
                            found_topics[topic] = {'grams': {gram:1},
                                                    'embedding_matched': wet,
                                                    'embedding_similarity': str_sim,
                                                    'gram_similarity':[sim],
                                                    'times': 1,
                                                    'topic':topic}



                        if sim == 1:
                            found_topics[topic]["syntactic"] = True



                        primary_label_topic = self.cso.get_primary_label_wu(topic)
                        if primary_label_topic not in explanation:
                            explanation[primary_label_topic] = set()

                        explanation[primary_label_topic].add(gram_without_underscore)

        return found_topics, explanation


    def __get_similar_words_from_cached_model(self, gram: str, grams: List[str]) -> List[Dict[str, Any]]:
        """ Getting similar words from the cached model
        Args:
            gram (str): the n-gram found (joined)
            grams (List[str]): list of tokens to be analysed and found in the model

        Returns:
            List[Dict[str, Any]]: containing of all found topics
        """
        if self.model.check_word_in_model(gram):
            list_of_matched_topics = self.model.get_words_from_model(gram)
        else:
            list_of_matched_topics = self.__match_ngram(grams)
        return list_of_matched_topics


    def __match_ngram(self, grams: List[str], merge: bool = True) -> List[Dict[str, Any]]:
        """
        Args:
            grams (List[str]): list of tokens to be analysed and found in the model
            merge (bool): Allows to combine the topics of multiple tokens, when analysing 2-grams or 3-grams. Defaults to True.

        Returns:
            List[Dict[str, Any]]: containing of all found topics
        """

        list_of_matched_topics = list()
        if len(grams) > 1 and merge:

            temp_list_of_matches = {}

            list_of_merged_topics = {}

            for gram in grams:
                if self.model.check_word_in_model(gram):
                    list_of_matched_topics_t = self.model.get_words_from_model(gram)
                    for topic_item in list_of_matched_topics_t:
                        temp_list_of_matches[topic_item["topic"]] = topic_item
                        try:
                            list_of_merged_topics[topic_item["topic"]] += 1
                        except KeyError:
                            list_of_merged_topics[topic_item["topic"]] = 1

            for topic_x, value in list_of_merged_topics.items():
                if value >= len(grams):
                    list_of_matched_topics.append(temp_list_of_matches[topic_x])

        return list_of_matched_topics


    def __get_similar_words_from_full_model(self, gram: str, grams: List[str]) -> List[Dict[str, Any]]:
        """ Getting similar words from the full model
        Args:
            gram (str): the n-gram found (joined)
            grams (List[str]): list of tokens to be analysed and found in the model

        Returns:
            List[Dict[str, Any]]: containing of all found topics
        """
        if self.model.check_word_in_full_model(gram):
            similar_words = self.model.get_top_similar_words_from_full_model(gram)

        else:
            similar_words = self.model.get_top_similar_words_from_full_model(grams)

        similar_words.append((gram,1))
        list_of_matched_topics = self.__refine_found_words(similar_words)

        return list_of_matched_topics

    def __refine_found_words(self, similar_words: List[Tuple[str, float]]) -> List[Dict[str, Any]]:
        """
        Args:
            similar_words (List[Tuple[str, float]]): list of tuples (word, similarity)

        Returns:
            List[Dict[str, Any]]: containing of all found topics
        """
        identified_topics = list()
        for word, sim in similar_words:
            topics = self.cso.find_closest_matches(word)
            for topic in topics:
                str_sim = Levenshtein.normalized_similarity(topic, word) #topic is from cso, wet is from word embedding
                if str_sim >= self.min_similarity:
                    identified_topics.append({"topic":topic,"sim_t":str_sim,"wet":word,"sim_w":sim})
        return identified_topics


    def __rank_topics(self, found_topics: Dict[str, Any], explanation: Dict[str, Set[str]]) -> Dict[str, float]:
        """ Function that ranks the list of found topics. It also cleans the explanation accordingly

        Args:
            found_topics (Dict[str, Any]): contains all information about the found topics
            explanation (Dict[str, Set[str]]): contains information about the explanation of topics

        Returns:
            Dict[str, float]: dictionary of final topics with their scores
        """
        max_value = 0
        scores = []
        for _,topic in found_topics.items():
            topic["score"] = topic["times"] * len(topic['grams'].keys())
            scores.append(topic["score"])
            if topic["score"] > max_value:
                max_value = topic["score"]

        for _,topic in found_topics.items():
            if "syntactic" in topic:
                topic["score"] = max_value




        # Selection of unique topics
        unique_topics = {}
        for t_p,topic in found_topics.items():
            prim_label = self.cso.get_primary_label_wu(t_p)
            if prim_label in unique_topics:
                if unique_topics[prim_label] < topic["score"]:
                    unique_topics[prim_label] = topic["score"]
            else:
                unique_topics[prim_label] = topic["score"]

        # ranking topics by their score. High-scored topics go on top
        sort_t = sorted(unique_topics.items(), key=lambda v: v[1], reverse=True)
        #sort_t = sorted(found_topics.items(), key=lambda k: k[1]['score'], reverse=True)


        # perform the elbow method
        vals = []
        for t_p in sort_t:
            vals.append(t_p[1]) #in 0, there is the topic, in 1 there is the info

        
        try: 
            while True:
                
                # cleaning the histogram for better calculation performance
                # If there are multiple topics with the same maximum score (a plateau at the top),
                # the knee locator might get confused. We remove the initial plateau to find the
                # actual drop in scores.
                if vals.count(max(vals)) > 1:
                    # Retain elements after the last occurrence of the maximum count
                    
                    # elegant version
                    # vals = vals[len(vals)-1-vals[::-1].index(max(vals)):] 
                    
                    
                    # efficient version (and certainly less elegant)
                    # This loop finds the index of the last element that equals the maximum value.
                    max_val = vals[0]
                    last_idx = 0
                    
                    for i in range(1, len(vals)):
                        if vals[i] < max_val:
                            break
                        last_idx = i
                    
                    # Slice the list to keep only the part starting from the drop.
                    vals = vals[last_idx:]
                    
                
                # Initialize KneeLocator to find the point of maximum curvature (the "elbow").
                # curve="convex" and direction="decreasing" are appropriate for a sorted score distribution.
                t_kn = KneeLocator(range(0,len(vals)), vals, S=1.0, curve="convex", direction="decreasing")
                try:
                    # If a valid knee is found (index > 0), we accept it.
                    if t_kn.knee > 0:
                        kneex = t_kn.knee
                        kneey = t_kn.knee_y
                        # print(f"Knee found at {kneex}, and it will select topics with score higher than {kneey}")
                        break
                    else:
                        # If knee is 0, it means the drop is immediate or the shape isn't ideal.
                        # We attempt to clean the histogram by removing the first element and recalculating.
                        # This acts as a retry mechanism to find a better knee point further down.
                        # Retain elements after the maximum count - 1
                        vals = vals[1:]
                        # print("Cleaning by decreasing of 1")
                except:
                    # Fallback in case of error (e.g., list is too short or empty).
                    # We default to selecting everything (kneey = 0) or the first element.
                    kneex = 0
                    kneey = vals[0] if vals else 0
                    # print("ended in this exception")
                    print(f"Knee found at {kneex}, and it will select topics with score higher than {kneey}")
                    break

        except:
            kneex = 0
            kneey = 0
            print(f"ERROR: Knee x:{kneex}; y:{kneey}; on an array of length: {len(sort_t)}")
            

        ##################### Pruning
        final_topics = {self.cso.get_topic_wu(sort_t[i][0]):(sort_t[i][1]/max_value) for i in range(len(sort_t)) if sort_t[i][1] >= kneey}
        self.reset_explanation()
        self.explanation = {self.cso.topics_wu[sort_t[i][0]]: explanation[sort_t[i][0]] for i in range(len(sort_t)) if sort_t[i][1] >= kneey}
            

            

        return final_topics
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
