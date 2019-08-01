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
import Levenshtein.StringMatcher as ls



class CSOClassifierSyntactic:
    """ An simple abstraction layer for using CSO classifier """

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
        
    
    def set_min__similarity(self, msm):
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
        """Function that splits the paper text in n-grams (unigrams,bigrams,trigrams)
        and with a Levenshtein it check the similarity for each of them with the topics in the ontology.

        Args:
            paper (string): The paper to analyse. At this stage it is a string.
            min_similarity (integer): minimum Levenshtein similarity between the n-gram and the topics within the CSO. 

        Returns:
            found_topics (dictionary): containing the found topics with their similarity and the n-gram analysed.
        """

        # analysing grams
        found_topics = {}
        
        idx = 0
        trigrams = ngrams(word_tokenize(paper, preserve_line=True), 3)
        matched_trigrams = []
        for grams in trigrams:
            idx += 1
            gram = " ".join(grams)
            topics = [key for key, _ in self.cso['topics'].items() if key.startswith(gram[:4])]
            for topic in topics:
                m = ls.StringMatcher(None, topic, gram).ratio()
                if m >= min_similarity:
                    topic = self.get_primary_label(topic, self.cso['primary_labels'])
                    if topic in found_topics:
                        found_topics[topic].append({'matched': gram, 'similarity': m})
                    else:
                        found_topics[topic] = [{'matched': gram, 'similarity': m}]
                    matched_trigrams.append(idx)
            
        
        idx = 0
        bigrams = ngrams(word_tokenize(paper, preserve_line=True), 2)
        matched_bigrams = []
        for grams in bigrams:
            idx += 1
            if (idx not in matched_trigrams) and ((idx-1) not in matched_trigrams):
                gram = " ".join(grams)
                topics = [key for key, _ in self.cso['topics'].items() if key.startswith(gram[:4])]
                for topic in topics:
                    m = ls.StringMatcher(None, topic, gram).ratio()
                    if m >= min_similarity:
                        topic = self.get_primary_label(topic, self.cso['primary_labels'])
                        if topic in found_topics:
                            found_topics[topic].append({'matched': gram, 'similarity': m})
                        else:
                            found_topics[topic] = [{'matched': gram, 'similarity': m}]
                        matched_bigrams.append(idx)
            

        idx = 0
        unigrams = ngrams(word_tokenize(paper, preserve_line=True), 1)
        for grams in unigrams:
            idx += 1
            if (idx not in matched_trigrams) and ((idx-1) not in matched_trigrams) and (idx not in matched_bigrams) and ((idx-1) not in matched_bigrams) and ((idx-1) not in matched_bigrams):
                gram = " ".join(grams)
                topics = [key for key, _ in self.cso['topics'].items() if key.startswith(gram[:4])]
                for topic in topics:
                    m = ls.StringMatcher(None, topic, gram).ratio()
                    if m >= min_similarity:
                        topic = self.get_primary_label(topic, self.cso['primary_labels'])
                        if topic in found_topics:
                            found_topics[topic].append({'matched': gram, 'similarity': m})
                        else:
                            found_topics[topic] = [{'matched': gram, 'similarity': m}]
            

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
    


    def get_primary_label(self, topic, primary_labels):
        """Function that returns the primary (preferred) label for a topic. If this topic belongs to 
        a cluster.

        Args:
            topic (string): Topic to analyse.
            primary_labels (dictionary): It contains the primary labels of all the topics belonging to clusters.

        Returns:
            topic (string): primary label of the analysed topic.
        """
        
        try:
            topic = primary_labels[topic]
        except KeyError:
            pass
        
        return topic