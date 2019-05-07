#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 14 14:43:42 2019

@author: angelosalatino
"""



# In[Loading Libraries]:


import classifier.classifier as CSO


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



# In[Run Classifier]

result = CSO.run_cso_classifier(paper)



# In[Printing and Saving]:


print(result)

with open('output.json', 'w') as outfile:
    json.dump(result, outfile, indent=4)

