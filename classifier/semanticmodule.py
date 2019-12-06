#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 22 11:38:18 2018

@author: angelosalatino
"""

from nltk import everygrams
from kneed import KneeLocator

import warnings

from classifier.preprocessing import part_of_speech_tagger, extraxt_chuncks


class CSOClassifierSemantic:
    """ A simple abstraction layer for using the Semantic module of the CSO classifier """
    
    def __init__(self, model = {}, cso = {}, paper = {}):
        """Function that initialises an object of class CSOClassifierSemantic and all its members.

        Args:
            model (dictionary): word2vec model.
            cso (dictionary): Computer Science Ontology
            paper (dictionary): paper{"title":"...","abstract":"...","keywords":"..."} the paper.

            
        """
        
        self.cso = cso                  #Stores the CSO Ontology
        self.paper = {}                 #Paper to analyse
        self.model = model        #contains the cached model
        self.set_paper(paper)           #Initialises the paper
        self.min_similarity = 0.94      #Initialises the min_similarity
        
        
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
        
    
    def set_min_similarity(self, min_similarity):
        """Function that initializes the minimum similarity variable.

        Args:
            min_similarity (float): value of min_similarity between 0 and 1.

        """
        self.min_similarity = min_similarity
 
    
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

        ##################### Tokenizer with spaCy.io
        pos_tags = part_of_speech_tagger(self.paper)
        
        ##################### Applying grammar          
        concepts = extraxt_chuncks(list(pos_tags))        

        ##################### Core analysis
        found_topics, topic_ngrams = self.find_topics(concepts)
    
        ##################### Ranking
        final_topics = self.rank_topics(found_topics) 
             
        return final_topics


    def find_topics(self, concepts):
        """Function that identifies topics starting from the ngram forund in the paper

        Args:
            ceoncepts (list): Chuncks of text to analyse.

        Returns:
            found_topics (dict): cdictionary containing the identified topics.
            successful_grams (dict): dictionary containing the ngrams that allowed to infer topics.
        """
        
        # Set up
        found_topics = {} # to store the matched topics
        successful_grams = {} # to store the successful grams

        # finding matches
        for concept in concepts:
            evgrams = everygrams(concept.split(), 1, 3) # list of unigrams, bigrams, trigrams
            for grams in evgrams:
                gram = "_".join(grams)
                
                #### Finding similar words contained in the model
                
                list_of_matched_topics = []

                if gram in self.model:
                    list_of_matched_topics = self.model[gram]
                    
                else:                    
                    list_of_matched_topics = self.match_ngram(grams)
                                    
                            
                for topic_item in list_of_matched_topics:
                        
                    topic = topic_item["topic"]
                    m     = topic_item["sim_t"]
                    wet   = topic_item["wet"]
                    sim   = topic_item["sim_w"]
                    
                    
                    if m >= self.min_similarity and topic in self.cso.topics_wu:
                        
    
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
                            if m > found_topics[topic]["embedding_similarity"]:
                                found_topics[topic]["embedding_similarity"] = m 
                                found_topics[topic]["embedding_matched"] = wet
    
                        else:
                            #creating new topic in the result set
                            found_topics[topic] = {'grams': {gram:1},
                                                    'embedding_matched': wet,
                                                    'embedding_similarity': m,
                                                    'gram_similarity':[sim],
                                                    'times': 1, 
                                                    'topic':topic}

                        
                        
                        if sim == 1:
                            found_topics[topic]["syntactic"] = True
    
    
                        # reporting successful grams: it is the inverse of found_topics["topic"]["grams"]
                        if gram in successful_grams:
                            successful_grams[gram].append(topic)
                        else:
                            successful_grams[gram] = [topic]
        
        return found_topics, successful_grams
    
    
    def match_ngram(self, grams, merge=True):
        """
        Args:
            grams ():
            merge (boolean): #Allows to combine the topics of mutiple tokens, when analysing 2-grams or 3-grams
        
        Returns:
            list_of_matched_topics (list): containing of all found topics 
        """
        
        list_of_matched_topics = list()
        if len(grams) > 1 and merge:
            
            temp_list_of_matches = {}
            
            list_of_merged_topics = {}
            
            for gram in grams:
                if gram in self.model:
                    list_of_matched_topics_t = self.model[gram]
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
                    
        
    def rank_topics(self, found_topics):
        
        max_value = 0
        scores = []
        for tp,topic in found_topics.items(): 
            topic["score"] = topic["times"] * len(topic['grams'].keys())
            scores.append(topic["score"])
            if topic["score"] > max_value:
                max_value = topic["score"]

        for tp,topic in found_topics.items():            
            if "syntactic" in topic:
                topic["score"] = max_value
                
                
             
            
        # Selection of unique topics  
        unique_topics = {}
        for tp,topic in found_topics.items():
            prim_label = self.cso.get_primary_label_wu(tp)
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
        for tp in sort_t:
            vals.append(tp[1]) #in 0, there is the topic, in 1 there is the info
        
        
        #### suppressing some warnings that can be raised by the kneed library
        warnings.filterwarnings("ignore")
        try:
            x = range(1,len(vals)+1) 
            kn = KneeLocator(x, vals, direction='decreasing')
            if kn.knee is None:
                #print("I performed a different identification of knee")
                kn = KneeLocator(x, vals, curve='convex', direction='decreasing')
        except ValueError:
            pass
        
        ##################### Pruning
        
        try: 
            knee = int(kn.knee)
        except TypeError:
            knee = 0
        except UnboundLocalError:
            knee = 0
            
        if knee > 5:
            try:
                knee += 0
            except TypeError:
                print("ERROR: ",kn.knee," ",knee, " ", len(sort_t))
            
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
        final_topics = [self.cso.topics_wu[sort_t[i][0]] for i in range(0,knee)]    

        return final_topics        
    
