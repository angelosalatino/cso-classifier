#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 23 15:17:24 2018

@author: angelosalatino
"""

import json
import cso_classifier as CSO

FILE = "ComputerScienceOntology.csv"
PAPER = {"title": "How are topics born? Understanding the research dynamics preceding the emergence of new areas",
         "abstract": "The ability to promptly recognise new research trends is strategic for many stakeholders, \
         including universities, institutional funding bodies, academic publishers and companies. \
         While the literature describes several approaches which aim to identify the emergence of new research \
         topics early in their lifecycle, these rely on the assumption that the topic in question is already \
         associated with a number of publications and consistently referred to by a community of researchers. \
         Hence, detecting the emergence of a new research area at an embryonic stage, i.e., before the topic has \
         been consistently labelled by a community of researchers and associated with a number of publications, \
         is still an open challenge. In this paper, we begin to address this challenge by performing a study \
         of the dynamics preceding the creation of new topics. This study indicates that the emergence of a \
         new topic is anticipated by a significant increase in the pace of collaboration between relevant \
         research areas, which can be seen as the ‘parents’ of the new topic. These initial findings (i) confirm \
         our hypothesis that it is possible in principle to detect the emergence of a new topic at the \
         embryonic stage, (ii) provide new empirical evidence supporting relevant theories in Philosophy of Science, \
         and also (iii) suggest that new topics tend to emerge in an environment in which weakly interconnected \
         research areas begin to cross-fertilise.", 
         "keywords": "Scholarly data, Topic emergence detection, Empirical study, Research trend detection, Topic discovery, Digital libraries"
         }
# PAPER = {"title": "Detection of Embryonic Research Topics by Analysing Semantic Topic Networks",
# 		"abstract": "Being aware of new research topics is an important asset for anybody involved in the research environment, including researchers, academic publishers and institutional funding bodies. In recent years, the amount of scholarly data available on the web has increased steadily, allowing the development of several approaches for detecting emerging research topics and assessing their trends. However, current methods focus on the detection of topics which are already associated with a label or a substantial number of documents. In this paper, we address instead the issue of detecting embryonic topics, which do not possess these characteristics yet. We suggest that it is possible to forecast the emergence of novel research topics even at such early stage and demonstrate that the emergence of a new topic can be anticipated by analysing the dynamics of pre-existing topics. We present an approach to evaluate such dynamics and an experiment on a sample of 3 million research papers, which confirms our hypothesis. In particular, we found that the pace of collaboration in sub-graphs of topics that will give rise to novel topics is significantly higher than the one in the control group.",
# 		"keywords": "Scholarly Data, Research Trend Detection, Topic Emergence Detection, Topic Discovery, Semantic Web, Ontology"
# 		}


def main():
    # load the computer science ontology from the file
    cso = CSO.load_cso(FILE)

    # provides the topics within the paper with an explanation
    result = CSO.cso_classifier(PAPER, cso, format='json', num_children=1, min_similarity=0.9, climb_ont='no', verbose=True)
    with open('result.json', 'w') as outfile:
        outfile.write(json.dumps(result))


if __name__ == '__main__':
    main()