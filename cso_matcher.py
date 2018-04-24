#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 23 15:16:13 2018

@author: angelosalatino
"""
import csv
import itertools
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk import ngrams
from nltk.tokenize import word_tokenize
import Levenshtein.StringMatcher as ls
    
   
def load_cso(file):
   
    with open(file) as ontoFile:
        topics = {}
        parents = {}
        same_as = {}
        ontology=csv.reader(ontoFile, delimiter=';')
        for triple in ontology:
            if(triple[1] == 'klink:broaderGeneric'):
                if(triple[2] in parents):
                    parents[triple[2]].append(triple[0])
                else:
                    parents[triple[2]] = [triple[0]]
            elif(triple[1] == 'klink:relatedEquivalent'):
                if(triple[2] in same_as):
                    same_as[triple[2]].append(triple[0])
                else:
                    same_as[triple[2]] = [triple[0]]
            elif(triple[1] == 'rdfs:label'):
                topics[triple[0]] = True
                
    cso = {'topics':topics, 'parents':parents, 'same_as':same_as}
            
    return(cso)
        
        

def cso_matcher(paper, cso, format="text", num_siblings=2, min_similarity=0.85):

    
    """
    Given a paper it returns the topics.
    paper = paper
    format = ['text','json']
    
    return the topics found in the text (found_topics)
    """
    if(format == 'json'):
        t_paper = paper
        paper = ""
        for key in list(t_paper.keys()):
            paper = paper + t_paper[key] + " "
            
            
    
    """ preprocessing
    """    
    paper = paper.lower()
    tokenizer = RegexpTokenizer(r'[\w\-\(\)]*')
    tokens = tokenizer.tokenize(paper)
    filtered_words = [w for w in tokens if not w in stopwords.words('english')]
    paper =  " ".join(filtered_words)
    
            
    """ analysing similarity with terms in the ontology
    """
    found_topics = statistic_similarity(paper,cso,min_similarity)
    
    """ extract more concepts from the ontology
    """
    found_topics = climb_ontology(found_topics,cso,num_siblings=num_siblings)

    return (found_topics)



def statistic_similarity(paper, cso, min_similarity):
    """ analysing grams
    """
    found_topics={}
    
    #result = [key for key, value in cso['topics'].items() if key.startswith("seman")]
    
    words = ngrams(word_tokenize(paper,preserve_line=True), 1)
    for grams in words:
        gram = " ".join(grams)
        topics = [key for key, _ in cso['topics'].items() if key.startswith(gram[:3])]
        for topic in topics:
            m = ls.StringMatcher(None, topic, gram).ratio()
            if(m >= min_similarity):
                if(topic in found_topics):
                    found_topics[topic].append({'matched':gram, 'similarity':m})
                else:
                    found_topics[topic] = [{'matched':gram, 'similarity':m}]

    bigrams = ngrams(word_tokenize(paper,preserve_line=True), 2)
    for grams in bigrams:
        gram = " ".join(grams)
        topics = [key for key, _ in cso['topics'].items() if key.startswith(gram[:3])]
        for topic in topics:
            m = ls.StringMatcher(None, topic, gram).ratio()
            if(m >= min_similarity):
                if(topic in found_topics):
                    found_topics[topic].append({'matched':gram, 'similarity':m})
                else:
                    found_topics[topic] = [{'matched':gram, 'similarity':m}] 
      
    trigrams = ngrams(word_tokenize(paper,preserve_line=True), 3)
    for grams in trigrams:
        gram = " ".join(grams)
        topics = [key for key, _ in cso['topics'].items() if key.startswith(gram[:3])]
        for topic in topics:
            m = ls.StringMatcher(None, topic, gram).ratio()
            if(m >= min_similarity):
                if(topic in found_topics):
                    found_topics[topic].append({'matched':gram, 'similarity':m})
                else:
                    found_topics[topic] = [{'matched':gram, 'similarity':m}]
            
    return (found_topics)


def climb_ontology(found_topics,cso,num_siblings):
    
    keys = list(found_topics.keys())
    combinations = itertools.combinations(range(len(keys)), num_siblings) # generates all possible combinations
    for combination in combinations:
        all_parents = {}
        for val in combination:
            if(keys[val] in cso['parents']):
                parents = cso['parents'][keys[val]]
                for parent in parents:
                    if(parent in all_parents):
                        ++all_parents[parent]
                    else:
                        all_parents[parent] = 1
                    
        for parent, times in all_parents.items():    
            if(times == num_siblings):
                if(parent not in found_topics):
                    found_topics[parent] = [{'matched':times, 'similarity':'null'}]
        all_parents.clear()
            
    return (found_topics)


def clear_explanation(found_topics, cso):
    topics = list(found_topics.keys()) 
    return topics