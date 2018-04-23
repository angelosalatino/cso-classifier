#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 23 15:16:13 2018

@author: angelosalatino
"""
   
def load_cso(file):
    import csv
    with open(file) as ontoFile:
        topics = {}
        parents = {}
        same_as = {}
        ontology=csv.reader(ontoFile, delimiter=';')
        for triple in ontology:
            if(triple[1] == 'klink:broaderGeneric'):
                if(triple[2] in parents):
                    parents[triple[2]].append([triple[0]])
                else:
                    parents[triple[2]] = [triple[0]]
            elif(triple[1] == 'klink:relatedEquivalent'):
                if(triple[2] in same_as):
                    same_as[triple[2]].append([triple[0]])
                else:
                    same_as[triple[2]] = [triple[0]]
            elif(triple[1] == 'rdfs:label'):
                topics[triple[0]] = True
                
    cso = {'topics':topics, 'parents':parents, 'same_as':same_as}
            
    return(cso)
        
        

def cso_matcher(paper, cso, format="text"):
    from nltk import ngrams
    from nltk.tokenize import word_tokenize
    
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
    
    found_topics=[]
    
    word = ngrams(word_tokenize(paper,preserve_line=True), 1)
    for grams in word:
      if(word in cso['topics']):
            found_topics.append(word) 

    bigrams = ngrams(word_tokenize(paper,preserve_line=True), 2)
    for grams in bigrams:
        if(" ".join(grams) in cso['topics']):
            found_topics.append(" ".join(grams)) 
      
    trigrams = ngrams(word_tokenize(paper,preserve_line=True), 3)
    for grams in trigrams:
        if(" ".join(grams) in cso['topics']):
            found_topics.append(" ".join(grams)) 

    

    return (found_topics)
