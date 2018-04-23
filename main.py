#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 23 15:17:24 2018

@author: angelosalatino
"""

import cso_matcher as CSO

file = "ComputerScienceOntology.csv"

cso = CSO.load_cso(file)

paper = {"title": "How are topics born? Understanding the research dynamics preceding the emergence of new areas",
         "abstract": "The ability to promptly recognise new research trends is strategic for many stakeholders, including universities, institutional funding bodies, academic publishers and companies. While the literature describes several approaches which aim to identify the emergence of new research topics early in their lifecycle, these rely on the assumption that the topic in question is already associated with a number of publications and consistently referred to by a community of researchers. Hence, detecting the emergence of a new research area at an embryonic stage, i.e., before the topic has been consistently labelled by a community of researchers and associated with a number of publications, is still an open challenge. In this paper, we begin to address this challenge by performing a study of the dynamics preceding the creation of new topics. This study indicates that the emergence of a new topic is anticipated by a significant increase in the pace of collaboration between relevant research areas, which can be seen as the ‘parents’ of the new topic. These initial findings (i) confirm our hypothesis that it is possible in principle to detect the emergence of a new topic at the embryonic stage, (ii) provide new empirical evidence supporting relevant theories in Philosophy of Science, and also (iii) suggest that new topics tend to emerge in an environment in which weakly interconnected research areas begin to cross-fertilise.",
         "keywords": "Scholarly data, Topic emergence detection, Empirical study, Research trend detection, Topic discovery, Digital libraries"
        }

paper = {"title": "semantic web artificial intelligence",
         "abstract": "Scholarly data, Topic emergence detection, Empirical study, Research trend detection, Topic discovery, Digital libraries"
        }

result = CSO.cso_matcher(paper, cso, format = 'json')

print(result)


