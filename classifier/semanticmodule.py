import warnings
from kneed import KneeLocator
import Levenshtein.StringMatcher as ls
from nltk import everygrams

class Semantic:
    """ A simple abstraction layer for using the Semantic module of the CSO classifier """

    def __init__(self, model = None, cso = None, fast_classification = True, paper = None):
        """Function that initialises an object of class CSOClassifierSemantic and all its members.

        Args:
            model (dictionary): word2vec model.
            cso (dictionary): Computer Science Ontology
            paper (dictionary): paper{"title":"...","abstract":"...","keywords":"..."} the paper.
        """
        self.cso = cso                  #Stores the CSO Ontology
        self.paper = paper              #Paper to analyse
        self.model = model              #contains the cached model
        self.min_similarity = 0.94      #Initialises the min_similarity
        self.fast_classification = fast_classification # if will use the full model or not
        self.explanation = dict()


    def set_paper(self, paper):
        """Function that initializes the paper variable in the class.

        Args:
            paper (either string or dictionary): The paper to analyse. It can be a full string in which the content
            is already merged or a dictionary  {"title": "","abstract": "","keywords": ""}.

        """
        self.paper = paper
        self.reset_explanation()


    def set_min_similarity(self, min_similarity):
        """Function that initializes the minimum similarity variable.

        Args:
            min_similarity (float): value of min_similarity between 0 and 1.

        """
        self.min_similarity = min_similarity


    def reset_explanation(self):
        """ Resetting the explanation
        """
        self.explanation = dict()


    def get_explanation(self):
        """ Returns the explanation
        """
        return self.explanation


    def classify_semantic(self):
        """Function that classifies the paper on a semantic level. This semantic module follows four steps:
            (i) entity extraction,
            (ii) CSO concept identification,
            (iii) concept ranking, and
            (iv) concept selection.

        Args:
            processed_embeddings (dictionary): This dictionary saves the matches between word embeddings and terms in CSO. It is useful when processing in batch mode.

        Returns:
            final_topics (list): list of identified topics.
        """

        ##################### Core analysis
        found_topics, explanation = self.__find_topics(self.paper.get_semantic_chunks())

        ##################### Ranking
        final_topics = self.__rank_topics(found_topics, explanation)

        return final_topics


    def __find_topics(self, concepts):
        """Function that identifies topics starting from the ngram forund in the paper

        Args:
            concepts (list): Chuncks of text to analyse.

        Returns:
            found_topics (dict): cdictionary containing the identified topics.
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


    def __get_similar_words_from_cached_model(self, gram, grams):
        """ Getting similar words from the cached model
        Args:
            gram (string): the n-gram found (joined)
            grams (list): list of tokens to be analysed and founf in the model

        Returns:
            list_of_matched_topics (list): containing of all found topics
        """
        if self.model.check_word_in_model(gram):
            list_of_matched_topics = self.model.get_words_from_model(gram)
        else:
            list_of_matched_topics = self.__match_ngram(grams)
        return list_of_matched_topics


    def __match_ngram(self, grams, merge=True):
        """
        Args:
            grams (list): list of tokens to be analysed and founf in the model
            merge (boolean): #Allows to combine the topics of mutiple tokens, when analysing 2-grams or 3-grams

        Returns:
            list_of_matched_topics (list): containing of all found topics
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


    def __get_similar_words_from_full_model(self, gram, grams):
        """ Getting similar words from the full model
        Args:
            gram (string): the n-gram found (joined)
            grams (list): list of tokens to be analysed and founf in the model

        Returns:
            list_of_matched_topics (list): containing of all found topics
        """
        if self.model.check_word_in_full_model(gram):
            similar_words = self.model.get_top_similar_words_from_full_model(gram)

        else:
            similar_words = self.model.get_top_similar_words_from_full_model(grams)

        similar_words.append((gram,1))
        list_of_matched_topics = self.__refine_found_words(similar_words)

        return list_of_matched_topics

    def __refine_found_words(self,similar_words):
        """
        Args:
            gram (string): the n-gram found (joined)
            grams (list): list of tokens to be analysed and founf in the model

        Returns:
            list_of_matched_topics (list): containing of all found topics
        """
        identified_topics = list()
        for word, sim in similar_words:
            topics = self.cso.find_closest_matches(word)
            for topic in topics:
                str_sim = ls.StringMatcher(None, topic, word).ratio() #topic is from cso, wet is from word embedding
                if str_sim >= self.min_similarity:
                    identified_topics.append({"topic":topic,"sim_t":str_sim,"wet":word,"sim_w":sim})
        return identified_topics


    def __rank_topics(self, found_topics, explanation):
        """ Function that ranks the list of found topics. It also cleans the explanation accordingly

        Args:
            found_topics (dictionary): contains all information about the found topics
            explanation (dictionary): contains information about the explanation of topics

        Returns:
            final_topics (list): list of final topics
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


        # perform
        vals = []
        for t_p in sort_t:
            vals.append(t_p[1]) #in 0, there is the topic, in 1 there is the info


        #### suppressing some warnings that can be raised by the kneed library
        warnings.filterwarnings("ignore")
        try:
            x_vals = range(1,len(vals)+1)
            t_kn = KneeLocator(x_vals, vals, direction='decreasing')
            if t_kn.knee is None:
                #print("I performed a different identification of knee")
                t_kn = KneeLocator(x_vals, vals, curve='convex', direction='decreasing')
        except ValueError:
            pass

        ##################### Pruning

        try:
            knee = int(t_kn.knee)
        except TypeError:
            knee = 0
        except UnboundLocalError:
            knee = 0

        if knee > 5:
            try:
                knee += 0
            except TypeError:
                print("ERROR: ",t_kn.knee," ",knee, " ", len(sort_t))

        else:
            try:
                if sort_t[0][1] == sort_t[4][1]:
                    top = sort_t[0][1]
                    test_topics = [item[1] for item in sort_t if item[1]==top]
                    knee = len(test_topics)

                else:
                    knee = 5
            except IndexError:
                knee = len(sort_t)

        final_topics = []
        final_topics = [self.cso.get_topic_wu(sort_t[i][0]) for i in range(0,knee)]
        self.reset_explanation()
        self.explanation = {self.cso.topics_wu[sort_t[i][0]]: explanation[sort_t[i][0]] for i in range(0,knee)}

        return final_topics
