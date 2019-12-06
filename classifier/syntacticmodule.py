#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 22 09:09:10 2018

@author: angelosalatino
"""
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk import ngrams
from nltk.tokenize import word_tokenize
from Levenshtein.StringMatcher import StringMatcher



class CSOClassifierSyntactic:
    """ A simple abstraction layer for using the Syntactic module of the CSO classifier """

    def __init__(self, cso = {}, paper = {}):
        """Function that initialises an object of class CSOClassifierSyntactic and all its members.

        Args:
            cso (dictionary): Computer Science Ontology
            paper (dictionary): paper{"title":"...","abstract":"...","keywords":"..."} the paper.

        """
        # Initialise variables to store CSO data - loads into memory 
        self.cso = cso
        self.min_similarity = 0.94
        self.paper = {}
        self.set_paper(paper)
    
    def set_paper(self, paper):
        """Function that initializes the paper variable in the class.

        Args:
            paper (either string or dictionary): The paper to analyse. It can be a full string in which the content
            is already merged or a dictionary  {"title": "","abstract": "","keywords": ""}.

        """

        try:
            if isinstance(paper, dict):
                t_paper = paper
                self.paper = ""
                try: 
                    for key in list(t_paper.keys()):
                        self.paper = self.paper + t_paper[key] + ". "
                except TypeError:
                    pass
                    print(paper)
        
                
                self.paper = self.paper.strip()
            elif isinstance(paper, str):
                self.paper = paper.strip()
            
            else:
                raise TypeError("Error: Field format must be either 'json' or 'text'")
                return
        except TypeError:
            pass
        
    
    def set_min_similarity(self, msm):
        """Function that sets a different value for the similarity.

        Args:
            msm (integer): similairity value.
        """
        self.min_similarity = msm

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


        # pre-processing
        paper = self.paper.lower()
        tokenizer = RegexpTokenizer(r'[\w\-\(\)]*')
        tokens = tokenizer.tokenize(paper)
        filtered_words = [w for w in tokens if w not in stopwords.words('english')]
        paper = " ".join(filtered_words)

        # analysing similarity with terms in the ontology
        extracted_topics = self.statistic_similarity(paper, self.min_similarity)
        
        topics = {}
        topics = self.strip_explanation(extracted_topics)
        
        
        return topics

        #shared_dict = topics
        
    def statistic_similarity(self, paper, min_similarity):
        
        found_topics = dict()
        matched_trigrams = set()
        matched_bigrams = set()
        
        for n in range(3, 0, -1):
            # i indexes the same token in the text whether we're matching by unigram, bigram, or trigram
            for i, grams in enumerate(ngrams(word_tokenize(paper, preserve_line=True), n)):
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
                    if match_ratio >= min_similarity:
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
                        
        return found_topics
    


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
