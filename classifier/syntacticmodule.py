from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk import ngrams
from nltk.tokenize import word_tokenize
from Levenshtein.StringMatcher import StringMatcher



class Syntactic:
    """ A simple abstraction layer for using the Syntactic module of the CSO classifier """

    def __init__(self, cso = None, paper = None):
        """Function that initialises an object of class CSOClassifierSyntactic and all its members.

        Args:
            cso (dictionary): Computer Science Ontology
            paper (Paper class): object containing the paper.

        """
        # Initialise variables to store CSO data - loads into memory 
        self.cso = cso
        self.min_similarity = 0.94
        self.paper = paper
        self.explanation = dict()

        
    
    def set_paper(self, paper):
        """Function that initializes the paper variable in the class.

        Args:
            paper (either string or dictionary): The paper to analyse. It can be a full string in which the content
            is already merged or a dictionary  {"title": "","abstract": "","keywords": ""}.

        """

        self.paper = paper
        self.explanation = dict()
        
    
    def set_min_similarity(self, msm):
        """Function that sets a different value for the similarity.

        Args:
            msm (integer): similairity value.
        """
        self.min_similarity = msm
      
        
    def reset_explanation(self):
        """ Resetting the explanation 
        """
        self.explanation = dict()
        
        
    def get_explanation(self):
        """ Returns the explanation 
        """
        return self.explanation
 

    def classify_syntactic(self):
        """Function that classifies a single paper. If you have a collection of papers, 
            you must call this function for each paper and organise the result.
           Initially, it cleans the paper file, removing stopwords (English ones) and punctuation.
           Then it extracts n-grams (1,2,3) and with a Levenshtein it check the similarity for each of
           them with the topics in the ontology.
           Next, it climbs the ontology, by selecting either the first broader topic or the whole set of
           broader topics until root is reached.

        Args:


        Returns:
            found_topics (dictionary): containing the found topics with their similarity and the n-gram analysed.
        """

        
        # analysing similarity with terms in the ontology
        extracted_topics = self.statistic_similarity(self.paper.get_chunks())
        
        final_topics = list()
        final_topics = self.strip_explanation(extracted_topics)
        
        return final_topics
        
        
    def statistic_similarity(self, concepts):
        
        found_topics = dict()
         
        for concept in concepts: 
            matched_trigrams = set()
            matched_bigrams = set()
            for comprehensive_grams in self.get_ngrams(concept):
                position = comprehensive_grams["position"]
                size = comprehensive_grams["size"]
                grams = comprehensive_grams["ngram"]
                # if we already matched the current token to a topic, don't reprocess it
                if position in matched_bigrams or position-1 in matched_bigrams:
                    continue           
                if position in matched_trigrams or position-1 in matched_trigrams or position-2 in matched_trigrams:
                    continue
                # otherwise unsplit the ngram for matching so ('quick', 'brown') => 'quick brown'
                gram = " ".join(grams)
                try:
                    # if there isn't an exact match on the first 4 characters of the ngram and a topic, move on
                    #topic_block = [key for key, _ in self.cso.topics.items() if key.startswith(gram[:4])]
                    topic_block = self.cso.topic_stems[gram[:4]]
                except KeyError:
                    continue
                for topic in topic_block:
                    # otherwise look for an inexact match
                    match_ratio = StringMatcher(None, topic, gram).ratio()
                    if match_ratio >= self.min_similarity:
                        try:
                            # if a 'primary label' exists for the current topic, use it instead of the matched topic
                            topic = self.cso.primary_labels[topic]
                        except KeyError:
                            pass
                        # note the tokens that matched the topic and how closely
                        if topic not in found_topics: 
                            found_topics[topic] = list()
                        found_topics[topic].append({'matched': gram, 'similarity': match_ratio})
                        # don't reprocess the current token
                        
                        if size == 2: matched_bigrams.add(position)
                        elif size == 3: matched_trigrams.add(position)
                        
                        # explanation bit
                        if topic not in self.explanation:
                            self.explanation[topic] = set()
                                                
                        self.explanation[topic].add(gram)
                        
        return found_topics
    
    def statistic_similarity2(self):
        
        found_topics = dict()
         
        for concept in self.paper.get_chunks(): 
            matched_trigrams = set()
            matched_bigrams = set()
            for n in range(3, 0, -1):
                # i indexes the same token in the text whether we're matching by unigram, bigram, or trigram
                for i, grams in enumerate(ngrams(word_tokenize(concept, preserve_line=True), n)):
                    # if we already matched the current token to a topic, don't reprocess it
                    if i in matched_bigrams or i-1 in matched_bigrams:
                        continue           
                    if i in matched_trigrams or i-1 in matched_trigrams or i-2 in matched_trigrams:
                        continue
                    # otherwise unsplit the ngram for matching so ('quick', 'brown') => 'quick brown'
                    gram = " ".join(grams)
                    try:
                        # if there isn't an exact match on the first 4 characters of the ngram and a topic, move on
                        #topic_block = [key for key, _ in self.cso.topics.items() if key.startswith(gram[:4])]
                        topic_block = self.cso.topic_stems[gram[:4]]
                    except KeyError:
                        continue
                    for topic in topic_block:
                        # otherwise look for an inexact match
                        match_ratio = StringMatcher(None, topic, gram).ratio()
                        if match_ratio >= self.min_similarity:
                            try:
                                # if a 'primary label' exists for the current topic, use it instead of the matched topic
                                topic = self.cso.primary_labels[topic]
                            except KeyError:
                                pass
                            # note the tokens that matched the topic and how closely
                            if topic not in found_topics: 
                                found_topics[topic] = list()
                            found_topics[topic].append({'matched': gram, 'similarity': match_ratio})
                            # don't reprocess the current token
                            
                            if n == 2: matched_bigrams.add(i)
                            elif n == 3: matched_trigrams.add(i)
                            
                            # explanation bit
                            if topic not in self.explanation:
                                self.explanation[topic] = set()
                                                    
                            self.explanation[topic].add(gram)
                        
        return found_topics
    
    def get_ngrams(self, concept):
        for n in range(3, 0, -1):
            pos = 0
            for ng in ngrams(word_tokenize(concept, preserve_line=True), n):
                yield {"position": pos, "size": n, "ngram": ng}
                pos += 1

    def strip_explanation(self, found_topics):
        """Function that removes statistical values from the dictionary containing the found topics.
            It returns only the topics. It removes the same as, picking the longest string in alphabetical order.

        Args:
            found_topics (dictionary): It contains the topics found with string similarity.

        Returns:
            topics (array): array containing the list of topics.
        """
        
        
        topics = list(set(found_topics.keys()))  # Takes only the keys
        
        return topics