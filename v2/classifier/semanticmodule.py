#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 22 11:38:18 2018

@author: angelosalatino
"""



import nltk
import re
from nltk import everygrams
import Levenshtein.StringMatcher as ls
from kneed import KneeLocator
import numpy as np
import spacy

class CSOClassifier:
    
    def __init__(self, model = {}, cso = {}, paper = {}):
        
        self.model = model
        self.cso = cso
        self.advsyntsema = {}
        self.set_paper(paper)

        
        
    def set_paper(self, paper):
        if isinstance(paper, dict):
            t_paper = paper
            self.paper = ""
            for key in list(t_paper.keys()):
                self.paper = self.paper + t_paper[key] + ". "
                
            self.paper = self.paper.strip()
        elif isinstance(paper, str):
            self.paper = paper.strip()
        
        else:
            raise TypeError("Error: Field format must be either 'json' or 'text'")
            return
    

        
        
 
    
    def classify_semantic(self, processed_embeddings={}):
        
        
        ##################### Tokenizer with spaCy.io
        
        nlp = spacy.load('en_core_web_sm')
        doc = nlp(self.paper)
        pos_tags_spacy = []
        for token in doc:
            if len(token.tag_) > 0:
                pos_tags_spacy.append((token.text, token.tag_))
                #print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,token.shape_, token.is_alpha, token.is_stop)
        
        pos_tags = pos_tags_spacy
        
        #print(pos_tags)
        
        ##################### Applying grammar
        
        GRAMMAR = "DBW_CONCEPT: {<JJ.*>*<NN.*>+}"
#        GRAMMAR = "DBW_CONCEPT: {<HYP.*|JJ.*>*<HYP.*|NN.*>+}"
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
        #processed_embeddings = {} # to store processed embeddings
        total_matched = 0
        word_similarity = 0.7 # similarity of words in the model
        top_amount_of_words = 10 # maximum number of words to select
        min_similarity = 0.94 #
        
                
        # finding matches
        for concept in concepts:
            evgrams = everygrams(concept.split(), 1, 3) # list of unigrams, bigrams, trigrams
            for grams in evgrams:
                gram = "_".join(grams)
        
                #### Finding similar words contained in the model
                #print("processing",gram)
                similarities = []
                
                similarities.append((gram,1)) #Appending the gram with max similarity
            
                try:
                    similarities_with_gram = self.get_top_similar_words(self.model.most_similar(gram,topn=top_amount_of_words), word_similarity)
                    similarities.extend(similarities_with_gram)
                except KeyError:
                    #print("Unigram: ",gram,"not found")
                    pass#continue
                
                if len(similarities) == 1 and len(grams) > 1: #if the model does not contain the gram, then it aims at analysing single words
                    try:    
                        similarities_with_grams = self.get_top_similar_words(self.model.most_similar(grams,topn=top_amount_of_words), word_similarity)
                        similarities.extend(similarities_with_grams)
                        #print("Processing N-Gram"," ".join(grams))
                    except KeyError:
                        #print("n-grams"," ".join(grams),"not found")
                        pass
                
                
                #if gram.startswith("data_mining"):
                    #print(similarities)
        
                #### Finding the words within CSO
                for wet, sim in similarities: #wet = word embedding topic, sim = similarity
                    
                    if sim >= word_similarity: # similarity on word embedding goes above threshold
                        
                        if wet in processed_embeddings:
                            # if this wet has already been processed in the past, we must know its most similar topic
                            topics = processed_embeddings[wet].keys() 
                            #print("I am grabbing the topics of ",wet)
                        else:
                            # looking for the topic within CSO
                            topics = [key for key, _ in self.cso['topics_wu'].items() if key.startswith(wet[:4])]
                            # in this position allows to keep track of all embeddings. The ones that fail will not have matches with topics in CSO
                            processed_embeddings[wet] = {} 
                            
                        for topic in topics:
                            #topic = topic.replace(" ", "_")
                            m = ls.StringMatcher(None, topic, wet).ratio() #topic is from cso, wet is from word embedding
                            if m >= min_similarity:
        
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
        
        
                                processed_embeddings[wet][topic] = m#True
        
        
        
                                total_matched += 1
        
        
        ##################### Ranking
        
        max_value = 0
        max_topic = ""
        scores = []
        for tp,topic in found_topics.items(): 
            topic["score"] = topic["times"] * len(topic['grams'].keys())
            scores.append(topic["score"])
            if topic["score"] > max_value:
                max_value = topic["score"]
                max_topic = topic["topic"]
            
        
        mean_total_scores = np.mean(scores)
        
        syntactic_match = 0
        for tp,topic in found_topics.items():            
            if "syntactic" in topic:
                topic["score"] = max_value
                
                
            #topic["score"] =  max_value - topic["score"]
#            if tp in topic["grams"]:
#                successful_grams_for_topic = list(set(successful_grams[tp]))
#                succ_scores = []
#                for succ_gram in successful_grams_for_topic:
#                    if succ_gram != tp:
#                        succ_scores.append(found_topics[succ_gram]["score"])
#                try:
#                    if(np.sum(succ_scores) >= mean_total_scores): #Checking if its semantic contribution is higher than the average
#                        topic["score"] = max_value
#                        syntactic_match += 1
#                except ValueError:
#                    pass
            
            #topic["score"] *= np.mean(topic["gram_similarity"]) 
             
            
        # Selection of unique topics  
        unique_topics = {}
        for tp,topic in found_topics.items():
            prim_label = self.get_primary_label(tp,self.cso["primary_labels_wu"])
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
        
        x = range(1,len(vals)+1) 
        kn = KneeLocator(x, vals, direction='decreasing')
        
        
        
        ##################### Pruning
        
        knee = int(kn.knee) 
        if knee > 5:
            try:
                knee += 0
            except TypeError:
                print(kn.knee," ",knee, " ", len(test_topics))
            
        else:
            
            if sort_t[0][1] == sort_t[4][1]:
                top = sort_t[0][1]
                test_topics = [item[1] for item in sort_t if item[1]==top] 
                knee = len(test_topics)
                print("I was here and I found knee = ",knee)
                print(sort_t)

            else:
                knee = 5

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
        #result = [y for (x,y) in enumerate(list_of_words) if y[1] >= th]
        result = [(x,y) for (x,y) in list_of_words if y >= th]
        return result
    
    
    def climb_ontology(self, found_topics):
        """Function that climbs the ontology. This function might retrieve
            just the first broader topic or the whole branch up until root

        Args:
            found_topics (dictionary): It contains the topics found with string similarity.
            cso (dictionary): the ontology previously loaded from the file.
            num_narrower (integer): it defines the number of narrower topics before their broader topic gets included
            in the final set of topics. Default = 2.
            climb_ont (string): either "jfb" or "wt" for selecting "just the first broader topic" or climbing
            the "whole tree".

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
            Otherwise an empty object.
            cso (dictionary): the ontology previously loaded from the file.

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
