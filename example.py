#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 23 15:17:24 2018

@author: angelosalatino
"""

import json
from skm3 import CSOClassifier as CSO

# Create an instance of the CSO_classifier class
clf = CSO(version=2)



paper1 = {
    "title": "How are topics born? Understanding the research dynamics preceding the emergence of new areas",
    "abstract": "The ability to promptly recognise new research trends is strategic for many stakeholders, " 
                "including universities, institutional funding bodies, academic publishers and companies. " 
                "While the literature describes several approaches which aim to identify the emergence of new research " 
                "topics early in their lifecycle, these rely on the assumption that the topic in question is already " 
                "associated with a number of publications and consistently referred to by a community of researchers. " 
                "Hence, detecting the emergence of a new research area at an embryonic stage, i.e., before the topic has " 
                "been consistently labelled by a community of researchers and associated with a number of publications, " 
                "is still an open challenge. In this paper, we begin to address this challenge by performing a study " 
                "of the dynamics preceding the creation of new topics. This study indicates that the emergence of a " 
                "new topic is anticipated by a significant increase in the pace of collaboration between relevant " 
                "research areas, which can be seen as the ‘parents’ of the new topic. These initial findings (i) confirm " 
                "our hypothesis that it is possible in principle to detect the emergence of a new topic at the " 
                "embryonic stage, (ii) provide new empirical evidence supporting relevant theories in Philosophy of Science, " 
                "and also (iii) suggest that new topics tend to emerge in an environment in which weakly interconnected " 
                "research areas begin to cross-fertilise.",
    "keywords": "Scholarly data, Topic emergence detection, Empirical study, Research trend detection, Topic "
                "discovery, Digital libraries"
                }


paper2 = {
    "title": "Detection of Embryonic Research Topics by Analysing Semantic Topic Networks",
    "abstract": "Being aware of new research topics is an important asset for anybody involved in the research "
                "environment, including researchers, academic publishers and institutional funding bodies. In recent "
                "years, the amount of scholarly data available on the web has increased steadily, allowing the "
                "development of several approaches for detecting emerging research topics and assessing their trends. "
                "However, current methods focus on the detection of topics which are already associated with a label or"
                " a substantial number of documents. In this paper, we address instead the issue of detecting "
                "embryonic topics, which do not possess these characteristics yet. We suggest that it is possible "
                "to forecast the emergence of novel research topics even at such early stage and demonstrate that "
                "the emergence of a new topic can be anticipated by analysing the dynamics of pre-existing topics. "
                "We present an approach to evaluate such dynamics and an experiment on a sample of 3 million "
                "research papers, which confirms our hypothesis. In particular, we found that the pace of "
                "collaboration in sub-graphs of topics that will give rise to novel topics is significantly "
                "higher than the one in the control group.",
    "keywords": "Scholarly Data, Research Trend Detection, Topic Emergence Detection, Topic Discovery, "
                "Semantic Web, Ontology"
                }

paper3 = {
    "title": "The Computer Science Ontology: A Large-Scale Taxonomy of Research Areas.",
    "abstract": "Ontologies of research areas are important tools for characterising, exploring, " 
                "and analysing the research landscape. Some fields of research are comprehensively described by " 
                "large-scale taxonomies, e.g., MeSH in Biology and PhySH in Physics. Conversely, current Computer " 
                "Science taxonomies are coarse-grained and tend to evolve slowly. For instance, the ACM classification " 
                "scheme contains only about 2K research topics and the last version dates back to 2012. In this paper, " 
                "we introduce the Computer Science Ontology (CSO), a large-scale, automatically generated ontology of " 
                "research areas, which includes about 26K topics and 226K semantic relationships. It was created by applying " 
                "the Klink-2 algorithm on a very large dataset of 16M scientific articles. CSO presents two main advantages over " 
                "the alternatives: i) it includes a very large number of topics that do not appear in other classifications, and ii) " 
                "it can be updated automatically by running Klink-2 on recent corpora of publications. CSO powers several tools adopted " 
                "by the editorial team at Springer Nature and has been used to enable a variety of solutions, such as classifying " 
                "research publications, detecting research communities, and predicting research trends. To facilitate the uptake of " 
                "CSO we have developed the CSO Portal, a web application that enables users to download, explore, and provide granular " 
                "feedback on CSO at different levels. Users can use the portal to rate topics and relationships, suggest missing " 
                "relationships, and visualise sections of the ontology. The portal will support the publication of and access to " 
                "regular new releases of CSO, with the aim of providing a comprehensive resource to the various communities engaged " 
                "with scholarly data.", 
    "keywords": "Scholarly Data, Ontology Learning, Bibliographic Data, Scholarly Ontologies."
    }


paper4 = {
    "title": "Klink-2: integrating multiple web sources to generate semantic topic networks.",
    "abstract": "The amount of scholarly data available on the web is steadily increasing, enabling " 
                "different types of analytics which can provide important insights into the research activity. " 
                "In order to make sense of and explore this large-scale body of knowledge we need an accurate, " 
                "comprehensive and up-to-date ontology of research topics. Unfortunately, human crafted classifications " 
                "do not satisfy these criteria, as they evolve too slowly and tend to be too coarse-grained. Current " 
                "automated methods for generating ontologies of research areas also present a number of limitations, " 
                "such as: i) they do not consider the rich amount of indirect statistical and semantic relationships, " 
                "which can help to understand the relation between two topics – e.g., the fact that two research areas are " 
                "associated with a similar set of venues or technologies; ii) they do not distinguish between different kinds " 
                "of hierarchical relationships; and iii) they are not able to handle effectively ambiguous topics characterized " 
                "by a noisy set of relationships. In this paper we present Klink-2, a novel approach which improves on our earlier " 
                "work on automatic generation of semantic topic networks and addresses the aforementioned limitations by taking " 
                "advantage of a variety of knowledge sources available on the web. In particular, Klink-2 analyses networks of " 
                "research entities (including papers, authors, venues, and technologies) to infer three kinds of semantic " 
                "relationships between topics. It also identifies ambiguous keywords (e.g., “ontology”) and separates them " 
                "into the appropriate distinct topics – e.g., “ontology/philosophy” vs. “ontology/semantic web”. Our experimental " 
                "evaluation shows that the ability of Klink-2 to integrate a high number of data sources and to generate topics with " 
                "accurate contextual meaning yields significant improvements over other algorithms in terms of both precision and recall.",
    "keywords": "Scholarly Data, Ontology Learning, Bibliographic Data, Scholarly Ontologies, Data Mining."
    }

def main():
    # Loads CSO data from local file
    clf.load_cso()

    # provides the topics within the paper with an explanation
    result = clf.classify(paper1, num_narrower=1, min_similarity=0.94, climb_ont='wt', verbose=False)
    with open('result.json', 'w') as outfile:
        outfile.write(json.dumps(result))


if __name__ == '__main__':
    """ Main entry point to the script """
    main()
