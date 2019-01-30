#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 22 08:45:29 2018

@author: angelosalatino
"""

import csv as co
import pickle
          
def load_cso():
        """Function that loads the CSO from the file in a dictionary.
           In particular, it load all the relationships organised in boxes:
               - topics, the list of topics
               - broaders, the list of broader topics for a given topic
               - narrowers, the list of narrower topics for a given topic
               - same_as, all the siblings for a given topic
               - primary_labels, all the primary labels of topics, if they belong to clusters

        Args:
            file (string): The path of the file constaining the ontology.

        Returns:
            cso (dictionary): {'topics':topics, 'broaders':broaders, 'narrowers':narrowers, 'same_as':same_as, 'primary_labels': primary_labels}.
        """

        with open('ontology/ComputerScienceOntology_v2.csv', 'r') as ontoFile:
            topics = {}
            broaders = {}
            narrowers = {}
            same_as = {}
            primary_labels = {}
            ontology = co.reader(ontoFile, delimiter=';')

            for triple in ontology:
                if triple[1] == 'klink:broaderGeneric':
                    # loading broader topics
                    if triple[2] in broaders:
                        broaders[triple[2]].append(triple[0])
                    else:
                        broaders[triple[2]] = [triple[0]]

                    # loading narrower topics
                    if triple[0] in narrowers:
                        narrowers[triple[0]].append(triple[2])
                    else:
                        narrowers[triple[0]] = [triple[2]]
                elif triple[1] == 'klink:relatedEquivalent':
                    if triple[2] in same_as:
                        same_as[triple[2]].append(triple[0])
                    else:
                        same_as[triple[2]] = [triple[0]]
                elif triple[1] == 'rdfs:label':
                    topics[triple[0].replace(" ", "_")] = triple[0]
                elif triple[1] == 'klink:primaryLabel':
                    primary_labels[triple[0].replace(" ", "_")] = triple[2].replace(" ", "_")

        cso = {
            'topics': topics,
            'broaders': broaders,
            'narrowers': narrowers,
            'same_as': same_as,
            'primary_labels': primary_labels
        }
        
        return cso


def get_primary_label(topic, primary_labels):
        """Function that returns the primary (preferred) label for a topic. If this topic belongs to 
        a cluster.

        Args:
            topic (string): Topic to analyse.
            primary_labels (dictionary): It contains the primary labels of all the topics belonging to clusters.

        Returns:
            topic (string): primary label of the analysed topic.
        """
        
        try:
            topic = primary_labels[topic]
        except KeyError:
            pass
        
        return topic
    
def get_top_similar_words(list_of_words, th):
    #result = [y for (x,y) in enumerate(list_of_words) if y[1] >= th]
    result = [(x,y) for (x,y) in list_of_words if y >= th]
    return result


def load_ontology_pickle():
    fcso = pickle.load( open( "classifier/models/cso.p", "rb" ) )
    return fcso


def load_ontology_and_model():
    fcso = pickle.load( open( "classifier/models/cso.p", "rb" ) )
    fmodel = pickle.load( open( "classifier/models/model.p", "rb" ) )
    return fcso, fmodel



def climb_ontology(cso, found_topics):
    """Function that climbs the ontology. This function might retrieve
        just the first broader topic or the whole branch up until root

    Args:
        found_topics (dictionary): It contains the topics found with string similarity.
        cso (dictionary): the ontology previously loaded from the file.
        num_narrower (integer): it defines the number of narrower topics before their broader topic gets included
        in the final set of topics. Default = 2.
        climb_ont (string): either "jfb" or "wt" for selecting "just the first broader topic" or climbing
        the "whole tree".

    Returns:
        found_topics (dictionary): containing the found topics with their similarity and the n-gram analysed.
    """

    all_broaders = {}
    inferred_topics = {}
    num_narrower = 1
    all_broaders = get_broader_of_topics(cso, found_topics, all_broaders)

    
    
    for broader, narrower in all_broaders.items():
        if len(narrower) >= num_narrower:
            broader = get_primary_label(broader, cso['primary_labels'])
            if broader not in inferred_topics:
                inferred_topics[broader] = [{'matched': len(narrower), 'broader of': narrower}]
            else:
                inferred_topics[broader].append({'matched': len(narrower), 'broader of': narrower})

    return list(set(inferred_topics.keys()).difference(found_topics))



def get_broader_of_topics(cso, found_topics, all_broaders):
    """Function that returns all the broader topics for a given set of topics.
        It analyses the broader topics of both the topics initially found in the paper, and the broader topics
        found at the previous iteration.
        It incrementally provides a more comprehensive set of broader topics.

    Args:
        found_topics (dictionary): It contains the topics found with string similarity.
        all_broaders (dictionary): It contains the broader topics found in the previous run.
        Otherwise an empty object.
        cso (dictionary): the ontology previously loaded from the file.

    Returns:
        all_broaders (dictionary): contains all the broaders found so far, including the previous iterations.
    """

    topics = list(found_topics)
    for topic in topics:
        if topic in cso['broaders']:
            broaders = cso['broaders'][topic]
            for broader in broaders:
                if broader in all_broaders:
                    if topic not in all_broaders[broader]:
                        all_broaders[broader].append(topic)
                    else:
                        pass  # the topic was listed before
                else:
                    all_broaders[broader] = [topic]

    return all_broaders