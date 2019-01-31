#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 15 22:59:48 2018

@author: angelosalatino
"""

import classifier.misc as misc
from classifier.syntacticmodule import CSOClassifier as synt
from classifier.semanticmodule import CSOClassifier as sema

import json



def re_classify():
    #load data
    with open('data/info.json', 'r') as handle:
        p = json.load(handle)
    
    class_res = {}
    processed_embeddings = {}
    paper = {}
    
    cso, model = misc.load_ontology_and_model()
    
    # Passing parematers to the two classes (synt and sem)
    synt_module = synt(cso)
    sema_module = sema(model, cso)
    
    
    for key, value in p.items():
        print("Processing:",key)
        paper["title"] = value["title"]
        paper["abstract"] = value["abstract"]
        paper["keywords"] = ', '.join(value["keywords"])
        synt_module.set_paper(paper)
        sema_module.set_paper(paper)
#        clf.set_paper(paper)
        
        process0 = synt_module.classify_syntactic()
        process1 = sema_module.classify_semantic(processed_embeddings)
        class_res[key] = {}
        class_res[key]["semantic"] = process1
        class_res[key]["syntactic"] = process0
        union = list(set(process0 + process1))
        class_res[key]["union"] = union
        enhanced = misc.climb_ontology(cso,union)
        class_res[key]["enhanced"] = [x for x in enhanced if x not in union]

    #save data
    with open('data/new_classification_complete_topics9Jan7.json', 'w') as outfile:
        json.dump(class_res, outfile, indent=4)


def main():

    re_classify()


if __name__ == '__main__':
    """ Main entry point to the script """
    main()
    