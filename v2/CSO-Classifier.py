#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 14 14:43:42 2019

@author: angelosalatino
"""



# In[Loading Libraries]:


import classifier.misc as misc
from classifier.syntacticmodule import CSOClassifierSyntactic as synt
from classifier.semanticmodule import CSOClassifierSemantic as sema

import json
 

# In[Loading Paper]:


paper = {
        "title": "De-anonymizing Social Networks",
        "abstract": "Operators of online social networks are increasingly sharing potentially "
        "sensitive information about users and their relationships with advertisers, application "
        "developers, and data-mining researchers. Privacy is typically protected by anonymization, "
        "i.e., removing names, addresses, etc. We present a framework for analyzing privacy and "
        "anonymity in social networks and develop a new re-identification algorithm targeting "
        "anonymized social-network graphs. To demonstrate its effectiveness on real-world networks, "
        "we show that a third of the users who can be verified to have accounts on both Twitter, a "
        "popular microblogging service, and Flickr, an online photo-sharing site, can be re-identified "
        "in the anonymous Twitter graph with only a 12% error rate. Our de-anonymization algorithm is "
        "based purely on the network topology, does not require creation of a large number of dummy "
        "\"sybil\" nodes, is robust to noise and all existing defenses, and works even when the overlap "
        "between the target network and the adversary's auxiliary information is small.",
        "keywords": "data mining, data privacy, graph theory, social networking (online)"
        }
        

print(paper["title"])
print(paper["abstract"])
print(paper["keywords"])



# In[Load Model, CSO and initialize]:


cso, model = misc.load_ontology_and_model()

# Passing parematers to the two classes (synt and sema)
synt_module = synt(cso, paper)
sema_module = sema(model, cso, paper)

#initializing variable that will contain output
class_res = {}



# In[Running]:


class_res["syntactic"] = synt_module.classify_syntactic()
class_res["semantic"]  = sema_module.classify_semantic()

union = list(set(class_res["syntactic"] + class_res["semantic"]))
class_res["union"] = union

enhanced = misc.climb_ontology(cso,union)
class_res["enhanced"] = [x for x in enhanced if x not in union]



# In[Printing and Saving]:


print(class_res)

with open('output.json', 'w') as outfile:
    json.dump(class_res, outfile, indent=4)

