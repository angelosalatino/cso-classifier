#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 22 11:38:18 2018

@author: angelosalatino
"""
import nltk
import re
from nltk import everygrams
from kneed import KneeLocator
import spacy
import warnings


class CSOClassifierSemantic:
    
    def __init__(self, model = {}, cso = {}, paper = {}):
        """Function that initialises an object of class CSOClassifierSemantic and all its members.

        Args:
            model (dictionary): word2vec model.
            cso (dictionary): Computer Science Ontology
            paper (dictionary): paper{"title":"...","abstract":"...","keywords":"..."} the paper.

            
        """
        
        self.cso = cso                  #Stores the CSO Ontology
        self.paper = {}                 #Paper to analyse
        self.ngrammerger = model        #contains the cached model
        self.merge_bigrams = True       #Allows to combine the topics of mutiple tokens, when analysing 2-grams or 3-grams
        self.set_paper(paper)           #Initialises the paper

        
        
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
        
        nlp = spacy.load('en_core_web_sm')
        doc = nlp(self.paper)
        pos_tags_spacy = []
        for token in doc:
            if len(token.tag_) > 0:
                pos_tags_spacy.append((token.text, token.tag_))
        
        pos_tags = pos_tags_spacy
        
        
        
        ##################### Applying grammar
        
        GRAMMAR = "DBW_CONCEPT: {<JJ.*>*<NN.*>+}"
        grammar_parser = nltk.RegexpParser(GRAMMAR)
        
        pos_tags_with_grammar = grammar_parser.parse(pos_tags)
        #print(pos_tags_with_grammar)
        concepts = []
        for node in pos_tags_with_grammar:
            if isinstance(node, nltk.tree.Tree) and node.label() == 'DBW_CONCEPT': # if matches our grammar 
                concept = ''
                for leaf in node.leaves():
                    concept_chunk = leaf[0]
                    concept_chunk = re.sub('[\=\,\…\’\'\+\-\–\“\”\"\/\‘\[\]\®\™\%]', ' ', concept_chunk)
                    concept_chunk = re.sub('\.$|^\.', '', concept_chunk)
                    concept_chunk = concept_chunk.lower().strip()
                    concept += ' ' + concept_chunk
                concept = re.sub('\.+', '.', concept)
                concept = re.sub('\s+', ' ', concept)
                concepts.append(concept)
        
        

        ##################### Core analysis
        
        # Set up
        found_topics = {} # to store the matched topics
        successful_grams = {} # to store the successful grams

        min_similarity = 0.94 #

        
        
        # finding matches
        for concept in concepts:
            evgrams = everygrams(concept.split(), 1, 3) # list of unigrams, bigrams, trigrams
            for grams in evgrams:
                gram = "_".join(grams)
                
                #### Finding similar words contained in the model
                
                list_of_matched_topics = []

                if gram in self.ngrammerger:
                    list_of_matched_topics = self.ngrammerger[gram]
                    
                else:
                    
                    if len(grams) > 1 and self.merge_bigrams:
                        
                        temp_list_of_matches = {}
                        
                        list_of_merged_topics = {}
                        
                        for gram in grams:
                            if gram in self.ngrammerger:
                                list_of_matched_topics_t = self.ngrammerger[gram]
                                for topic_item in list_of_matched_topics_t:
                                    temp_list_of_matches[topic_item["topic"]] = topic_item
                                    try:
                                        list_of_merged_topics[topic_item["topic"]] += 1
                                    except KeyError:
                                        list_of_merged_topics[topic_item["topic"]] = 1
                                    
                        for topic_x, value in list_of_merged_topics.items():
                            if value >= len(grams):
                                list_of_matched_topics.append(temp_list_of_matches[topic_x])
                                    
                            
                for topic_item in list_of_matched_topics:
                        
                    topic = topic_item["topic"]
                    m     = topic_item["sim_t"]
                    wet   = topic_item["wet"]
                    sim   = topic_item["sim_w"]
                    
                    
                    if m >= min_similarity and topic in self.cso["topics_wu"]:
                        
    
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
    
    
                
        
        ##################### Ranking
        
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
            prim_label = self.get_primary_label(tp,self.cso["primary_labels_wu"])
            if prim_label == 'network_structures':
                print('Here I found you:', tp)
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
        final_topics = [self.cso["topics_wu"][sort_t[i][0]] for i in range(0,knee)]
        
             
        return final_topics

    
    
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
    
    def get_top_similar_words(self, list_of_words, th):
        """Function that identifies the top similar words in the model that have similarity higher than th.

        Args:
            list_of_words (list of tuples): It contains the topics found with string similarity.
            th (integer): threshold

        Returns:
            result (dictionary): containing the found topics with their similarity and the n-gram analysed.
        """
        #result = [y for (x,y) in enumerate(list_of_words) if y[1] >= th]
        result = [(x,y) for (x,y) in list_of_words if y >= th]
        return result
    
    
    def climb_ontology(self, found_topics):
        """Function that climbs the ontology. This function might retrieve
            just the first broader topic or the whole branch up until root

        Args:
            found_topics (dictionary): It contains the topics found with string similarity.


        Returns:
            found_topics (dictionary): containing the found topics with their similarity and the n-gram analysed.
        """

        all_broaders = {}
        inferred_topics = {}
        num_narrower = 1
        all_broaders = self.get_broader_of_topics(found_topics, all_broaders)

        
        
        for broader, narrower in all_broaders.items():
            if len(narrower) >= num_narrower:
                broader = self.get_primary_label(broader, self.cso['primary_labels'])
                if broader not in inferred_topics:
                    inferred_topics[broader] = [{'matched': len(narrower), 'broader of': narrower}]
                else:
                    inferred_topics[broader].append({'matched': len(narrower), 'broader of': narrower})

        return list(set(inferred_topics.keys()).difference(found_topics))
    
    
    def get_broader_of_topics(self, found_topics, all_broaders):
        """Function that returns all the broader topics for a given set of topics.
            It analyses the broader topics of both the topics initially found in the paper, and the broader topics
            found at the previous iteration.
            It incrementally provides a more comprehensive set of broader topics.

        Args:
            found_topics (dictionary): It contains the topics found with string similarity.
            all_broaders (dictionary): It contains the broader topics found in the previous run.

        Returns:
            all_broaders (dictionary): contains all the broaders found so far, including the previous iterations.
        """

        topics = list(found_topics)
        for topic in topics:
            if topic in self.cso['broaders']:
                broaders = self.cso['broaders'][topic]
                for broader in broaders:
                    if broader in all_broaders:
                        if topic not in all_broaders[broader]:
                            all_broaders[broader].append(topic)
                        else:
                            pass  # the topic was listed before
                    else:
                        all_broaders[broader] = [topic]

        return all_broaders
    
