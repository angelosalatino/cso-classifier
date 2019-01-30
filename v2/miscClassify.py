#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 15 23:01:40 2018

@author: angelosalatino
"""



import hashlib

## external functions
import classifier.misc as misc
from classifier.functions.stringmatcher import CSOClassifier as sm
from classifier.functions.word_embeddings import CSOSemanticClassifier as we


def get_paper(papers,key):
    value = papers[key]
    paper = {}
    paper["title"] = value["title"]
    paper["abstract"] = value["abstract"]
    paper["keywords"] = ', '.join(value["keywords"])
    return paper


def classify_papers_batch1(p):
    
    class_res = {}
    processed_embeddings = {}
    paper = {}
    
    cso, model = misc.load_ontology_and_model()
    
    # Passing parematers to the two classes (synt and sem)
    clf2 = we(model, cso)
    
    
    for key, value in p.items():
        print("Processing:",key)
        paper["title"] = value["title"]
        paper["abstract"] = value["abstract"]
        paper["keywords"] = ', '.join(value["keywords"])
        clf2.set_paper(paper)
        
        
        process = clf2.classify_with_nlp(processed_embeddings)
        class_res[key] = process

        
    
    return class_res

def classify_papers_batchHybrid(p):
    
    class_res = {}
    processed_embeddings = {}
    paper = {}
    
    cso, model = misc.load_ontology_and_model()
    
    # Passing parematers to the two classes (synt and sem)
    clf2 = we(model, cso)
    clf = sm(cso)
    
    
    for key, value in p.items():
        print("Processing:",key)
        paper["title"] = value["title"]
        paper["abstract"] = value["abstract"]
        paper["keywords"] = ', '.join(value["keywords"])
        clf2.set_paper(paper)
#        clf.set_paper(paper)
        
        process0 = clf.classify2(paper, num_narrower=1, min_similarity=0.94, climb_ont='wt', verbose=False)
        process1 = clf2.classify_with_nlp(processed_embeddings)
        class_res[key] = {}
        class_res[key]["semantic"] = process1["extracted"]
        class_res[key]["syntactic"] = process0["extracted"]
        union = list(set(process0["extracted"]+process1["extracted"]))
        class_res[key]["union"] = union
        enhanced = get_broader_topics(cso,union)
        class_res[key]["enhanced"] = [x for x in enhanced if x not in union]
        
        

        
    
    return class_res


def classify_paper(papers,key):
    
    class_res = {}
    processed_embeddings = {}
    paper = {}
    

    
    if key in papers:
        cso, model = misc.load_ontology_and_model()
    
        # Passing parematers to the two classes (synt and sem)
        clf2 = we(model, cso)
        value = papers[key]
        print("Processing:",key)
        paper["title"] = value["title"]
        paper["abstract"] = value["abstract"]
        paper["keywords"] = ', '.join(value["keywords"])
        clf2.set_paper(paper)
        
        
        process = clf2.classify_with_nlp(processed_embeddings)
        class_res[key] = process
    else:
        print(key,"not found")
    


        
    
    return class_res


def get_broader_topics(cso,list_of_topics):
    return misc.climb_ontology(cso,list_of_topics)
