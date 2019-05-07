#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  7 17:19:22 2019

@author: angelosalatino
"""



# In[Loading Libraries]:


import classifier.misc as misc
from classifier.syntacticmodule import CSOClassifierSyntactic as synt
from classifier.semanticmodule import CSOClassifierSemantic as sema


def run_cso_classifier(paper, modules = "both", enhancement = "first"): 
    """Function that runs the CSO Classifier. 
    The ontology file has been serialised with Pickle. 
    The cached model is a json file (dictionary) containing all words in the corpus vocabulary with the corresponding CSO topics.
    The latter has been created to speed up the process of retrieving CSO topics given a token in the metadata
    

    Args:
        paper (dictionary): contains the metadata of the paper, e.g., title, abstract and keywords {"title": "","abstract": "","keywords": ""}.
        modules (string): either "syntactic", "semantic" or "both" to determine which modules to use when classifying. "syntactic" enables only the syntactis module. "semantic" enables only the semantic module. Finally, with "both" the classifier takes advantage of both the syntactic and semantic modules. Default = "both".
        enhances (string): 
    Returns:
        fcso (dictionary): contains the CSO Ontology.
        fmodel (dictionary): contains a cache of the model, i.e., each token is linked to the corresponding CSO topic.
    """
    
    if modules not in ["syntactic", "semantic", "both"]:
        raise ValueError("Error: Field modules must be 'syntactic', 'semantic' or 'both'")
        return
    
    if enhancement not in ["first", "all", "no"]:
        raise ValueError("Error: Field enhances must be 'first', 'all' or 'no'")
        return
    
    # Loading ontology and model
    cso, model =  misc.load_ontology_and_chached_model()
    
    # Passing parematers to the two classes (synt and sema)
    synt_module = synt(cso, paper)
    sema_module = sema(model, cso, paper)
    
    #initializing variable that will contain output
    class_res = dict()
    class_res["syntactic"] = list()
    class_res["semantic"] = list()
    class_res["union"] = list()
    class_res["enhanced"] = list()
    
    
    if modules == 'syntactic' or modules == 'both':
        class_res["syntactic"] = synt_module.classify_syntactic()
    if modules == 'semantic' or modules == 'both':
        class_res["semantic"]  = sema_module.classify_semantic()
    
    union = list(set(class_res["syntactic"] + class_res["semantic"]))
    class_res["union"] = union
    
    
    if enhancement == 'first':
        enhanced = misc.climb_ontology(cso,union, "first")
        class_res["enhanced"] = [x for x in enhanced if x not in union]
    elif enhancement == 'all':
        enhanced = misc.climb_ontology(cso,union, "all")
        class_res["enhanced"] = [x for x in enhanced if x not in union]
    elif enhancement == 'no':
        pass


    return class_res

