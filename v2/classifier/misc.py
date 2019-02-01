#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 22 08:45:29 2018

@author: angelosalatino

This file mostly contains routines to deal with the Computer Science Ontology and the model.
"""

import pickle
import os
import sys
import requests
from hurry.filesize import size

def load_ontology_pickle():
    """Function that loads CSO. 
    This file has been serialised using Pickle allowing to be loaded quickly.
    
    Args:

    Returns:
        fcso (dictionary): containing the found topics with their similarity and the n-gram analysed.
    """
    fcso = pickle.load( open( "classifier/models/cso.p", "rb" ) )
    return fcso


def load_ontology_and_model():
    """Function that loads both CSO and Word2vec model. 
    Those two files have been serialised using Pickle allowing to be loaded quickly.
    

    Args:

    Returns:
        fcso (dictionary): containing the found topics with their similarity and the n-gram analysed.
        fmodel (dictionary): containing the found topics with their similarity and the n-gram analysed.
    """
    
    check_model()
    
    fcso = pickle.load( open( "classifier/models/cso.p", "rb" ) )
    fmodel = pickle.load( open( "classifier/models/model.p", "rb" ) )
    
    print("Computer Science Ontology and Word2vec model loaded.")
    return fcso, fmodel
      

def check_model():
    """Function that checks if the model is available. If not, it will attempt to download it from a remote location.
    Tipically hosted on the CSO Portal

    """
    
    path = 'classifier/models/model.p'
    url = 'https://cso.kmi.open.ac.uk/download/model.p'  
    if not os.path.exists(path):
        print('[*] Beginning model download from',url)
        download_file(url, path)  
        
        
def download_file(url, filename):
    """Function that downloads the model from the web.

    Args:
        url (string): Url of where the model is located.
        filename (string): location of where to save the model

    Returns:
        
    """
    with open(filename, 'wb') as f:
        response = requests.get(url, stream=True)
        total = response.headers.get('content-length')

        if total is None:
            f.write(response.content)
        else:
            downloaded = 0
            total = int(total)
            for data in response.iter_content(chunk_size=max(int(total/1000), 1024*1024)):
                downloaded += len(data)
                f.write(data)
                done = int(50*downloaded/total)
                sys.stdout.write('\r[{}{}] {}/{}'.format('█' * done, '.' * (50-done), size(downloaded), size(total)))
                sys.stdout.flush()
    sys.stdout.write('\n')
    print('[*] Done!')


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