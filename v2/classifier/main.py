#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 22 08:36:40 2018

@author: angelosalatino
"""


import datetime
import json
import hashlib

## external functions
import misc
from functions.stringmatcher import CSOClassifier as sm
from functions.word_embeddings import CSOSemanticClassifier as we
import multiprocessing as mp

## testing import (to be deleted once in deploy)

paper = {
    "title": "Klink-2: integrating multiple web sources to generate semantic topic networks..",
    "abstract": "The amount of scholarly data available on the web is steadily increasing, enabling " 
                "different types of analytics which can provide important insights into the research activity. " 
                "In order to make sense of and explore this large-scale body of knowledge we need an accurate,    ",
    "keywords": "Scholarly Data, Ontology Learning, Bibliographic Data, Scholarly Ontologies, Data Mining."
    }




doi = "https://dl.acm.org/citation.cfm?id=944937"

def main():
    a = datetime.datetime.now()
    
    # Loads CSO data from local file
    cso, model = misc.load_ontology_and_model()
    
    # Passing parematers to the two classes (synt and sem)
    clf = sm(cso, paper)
    clf2 = we(model, cso, paper)
    
    # Creating shared structure
    manager = mp.Manager()
    shared_dict = manager.dict()

    
    # Initialising processes
    processes1 = clf.run(shared_dict)
    processes2 = clf2.run(shared_dict)
    processes = processes1 + processes2
    
    # Running Processes
    [x.start() for x in processes]
    [x.join() for x in processes]
    [x.terminate() for x in processes]
    
    result = {}
    
    result['stringmatcher'] = {}
    result['stringmatcher']["extracted"] = []
    result['stringmatcher']["inferred"] = []
    
    result['stringsimilarity'] = {}
    result['stringsimilarity']["extracted"] = []
    result['stringsimilarity']["inferred"] = []
    
    result['syntsema'] = {}
    result['syntsema']["extracted"] = []
    result['syntsema']["inferred"] = []
    
    result['advsyntsema'] = {}
    result['advsyntsema']["extracted"] = []
    result['advsyntsema']["inferred"] = []
    
    if 'stringmatcher' in shared_dict:
        result['stringmatcher'] = shared_dict['stringmatcher']
       
    if 'stringsimilarity' in shared_dict:
        result['stringsimilarity'] = shared_dict['stringsimilarity']
        
    if 'syntsema' in shared_dict:
        result['syntsema'] = shared_dict['syntsema']

    if 'advsyntsema' in shared_dict:
        result['advsyntsema'] = shared_dict['advsyntsema']

    
    # Joining the structures
    result["unique"] = list(set(
                        result["stringmatcher"]["extracted"] + result["stringmatcher"]["inferred"] + 
                        result["stringsimilarity"]["extracted"] + result["stringsimilarity"]["inferred"] +
                        result["syntsema"]["extracted"] + result["syntsema"]["inferred"] +
                        result["advsyntsema"]["extracted"] + result["advsyntsema"]["inferred"]
                        ))
    
    
    ## LOG analysed paper
    z = {**paper, **result}
    z["doi"] = doi
    
    filename = hashlib.md5(doi.encode()).hexdigest()
    with open('papers/'+filename, 'w') as outfile:
        json.dump(z, outfile)
    
    b = datetime.datetime.now()
    delta = b - a
    print(delta)
    
    
    print(json.dumps(result, indent=2, sort_keys=False))
    
    
#    result = {}
#    result["syntsema"]         = clf2.get_syntsema()
#    result["advsyntsema"]      = clf2.get_advsyntsema()
    
#    result = {} 
#    rt = clf.classify(paper, num_narrower=1, min_similarity=1, climb_ont='wt', verbose=False)
#    result["stringmatcher"]    = rt
#    rt = clf.classify(paper, num_narrower=1, min_similarity=0.94, climb_ont='wt', verbose=False)
#    result["stringsimilarity"] = rt
#    result["syntsema"]         = clf2.classify_with_window()
#    result["advsyntsema"]      = clf2.classify_with_nlp()
#    
#    
#    
#    result["unique"] = list(set(
#                        result["stringmatcher"]["extracted"] + result["stringmatcher"]["inferred"] + 
#                        result["stringsimilarity"]["extracted"] + result["stringsimilarity"]["inferred"] +
#                        result["syntsema"]["extracted"] + result["syntsema"]["inferred"] +
#                        result["advsyntsema"]["extracted"] + result["advsyntsema"]["inferred"]
#                        ))
    
#    manager = multiprocessing.Manager()
#    result = manager.dict()
#    jobs = []
#    
#    p1 = multiprocessing.Process(target=clf.classify, args=(paper, 1, 1, 'wt', False, result["stringmatcher"]))
#    jobs.append(p1)
#    p1.start()
#    
#    p2 = multiprocessing.Process(target=clf.classify, args=(paper, 1, 0.94, 'wt', False, result["stringsimilarity"]))
#    jobs.append(p2)
#    p2.start()
#    
#    p3 = multiprocessing.Process(target=clf2.classify_with_window, args=(paper, result["syntsema"]))
#    jobs.append(p3)
#    p3.start()
#    
#    p4 = multiprocessing.Process(target=clf2.classify_with_nlp, args=(paper, result["advsyntsema"]))
#    jobs.append(p4)
#    p4.start()
#    
#    for proc in jobs:
#        proc.join()
#    
    
#    result = {}
#    rt1 = clf.classify(paper, num_narrower=1, min_similarity=1, climb_ont='wt', verbose=False)
#    rt2 = clf.classify(paper, num_narrower=1, min_similarity=0.94, climb_ont='wt', verbose=False)
#    rt3 = clf2.classify_with_window(paper)
#    rt4 = clf2.classify_with_nlp(paper)
#    result["stringmatcher"]    = rt1
#    result["stringsimilarity"] = rt2
#    result["syntsema"]         = rt3
#    result["advsyntsema"]      = rt4
#    
    
    
    
    
#    result["unique"] = list(set(
#                        result["stringmatcher"]["extracted"] + result["stringmatcher"]["inferred"] + 
#                        result["stringsimilarity"]["extracted"] + result["stringsimilarity"]["inferred"] +
#                        result["syntsema"]["extracted"] + result["syntsema"]["inferred"] +
#                        result["advsyntsema"]["extracted"] + result["advsyntsema"]["inferred"]
#                        ))
#    
#    
#   
    
    
    
    
    




if __name__ == '__main__':
    """ Main entry point to the script """
    main()
