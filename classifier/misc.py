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
import networkx as nx
from webweb import Web
import numpy as np
from hurry.filesize import size
import csv as co
import json
from itertools import islice

#some global variables
dir = os.path.dirname(os.path.realpath(__file__))
CSO_PATH = f"{dir}/models/cso.csv"
CSO_PICKLE_PATH = f"{dir}/models/cso.p"
CSO_REMOTE_URL = "https://cso.kmi.open.ac.uk/download/cso.csv"
MODEL_PICKLE_PATH = f"{dir}/models/model.p"
MODEL_PICKLE_REMOTE_URL = "https://cso.kmi.open.ac.uk/download/model.p"
CACHED_MODEL = f"{dir}/models/token-to-cso-combined.json"
CACHED_MODEL_REMOTE_URL = "https://cso.kmi.open.ac.uk/download/token-to-cso-combined.json"

def load_cso():
    """Function that loads the CSO from the file in a dictionary.
       In particular, it load all the relationships organised in boxes:
           - topics, the list of topics
           - broaders, the list of broader topics for a given topic
           - narrowers, the list of narrower topics for a given topic
           - same_as, all the siblings for a given topic
           - primary_labels, all the primary labels of topics, if they belong to clusters
           - topics_wu, topic with underscores
           - primary_labels_wu, primary labels with underscores

    Args:
        

    Returns:
        cso (dictionary): {'topics':topics, 'broaders':broaders, 'narrowers':narrowers, 'same_as':same_as, 'primary_labels': primary_labels}.
    """

    with open(CSO_PATH, 'r') as ontoFile:
        topics = {}
        topics_wu = {}
        broaders = {}
        narrowers = {}
        same_as = {}
        primary_labels = {}
        primary_labels_wu = {}
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
                topics[triple[0]] = True
                topics_wu[triple[0].replace(" ", "_")] = triple[0]
            elif triple[1] == 'klink:primaryLabel':
                primary_labels[triple[0]] = triple[2]
                primary_labels_wu[triple[0].replace(" ", "_")] = triple[2].replace(" ", "_")

    cso = {
        'topics': topics,
        'broaders': broaders,
        'narrowers': narrowers,
        'same_as': same_as,
        'primary_labels': primary_labels,
        'topics_wu': topics_wu,
        'primary_labels_wu': primary_labels_wu
    }
    
        
        
    return cso
        

def load_token2cso_merger():
    #print("Loading Model to CSO Merger")
    with open(CACHED_MODEL) as f:
       return json.load(f)



def load_ontology_pickle():
    """Function that loads CSO. 
    This file has been serialised using Pickle allowing to be loaded quickly.
    
    Args:

    Returns:
        fcso (dictionary): contains the CSO Ontology.
    """
    check_ontology()
    fcso = pickle.load( open( CSO_PICKLE_PATH, "rb" ) )
    return fcso


def load_ontology_and_model():
    """Function that loads both CSO and Word2vec model. 
    Those two files have been serialised using Pickle allowing to be loaded quickly.
    

    Args:

    Returns:
        fcso (dictionary): contains the CSO Ontology.
        fmodel (dictionary): contains the word2vec model.
    """
    
    check_ontology()
    check_model()
    
    fcso = pickle.load( open( CSO_PICKLE_PATH, "rb" ) )
    fmodel = pickle.load( open( MODEL_PICKLE_PATH, "rb" ) )
    
    print("Computer Science Ontology and Word2vec model loaded.")
    return fcso, fmodel


def load_ontology_and_chached_model():
    """Function that loads both CSO and the cached Word2vec model. 
    The ontology file has been serialised with Pickle. 
    The cached model is a json file (dictionary) containing all words in the corpus vocabulary with the corresponding CSO topics.
    The latter has been created to speed up the process of retrieving CSO topics given a token in the metadata
    

    Args:

    Returns:
        fcso (dictionary): contains the CSO Ontology.
        fmodel (dictionary): contains a cache of the model, i.e., each token is linked to the corresponding CSO topic.
    """
    
    check_ontology()
    check_cached_model()
    
    fcso = pickle.load( open( CSO_PICKLE_PATH, "rb" ) )
    
    with open(CACHED_MODEL) as f:
       fmodel =  json.load(f)
    
    print("Computer Science Ontology and cached model loaded.")
    return fcso, fmodel

     
def check_ontology():
    """Function that checks if the ontology is available. 
    If not, it will check if a csv version exists and then it will create the pickle file.
    
    """ 
    
    if not os.path.exists(CSO_PICKLE_PATH):
        print("Ontology pickle file is missing.")
        
        if not os.path.exists(CSO_PATH):
            print("The csv file of the Computer Science Ontology is missing. Attempting to download it now...")
            download_file(CSO_REMOTE_URL, CSO_PATH) 
        
        cso = load_cso()
        
        with open(CSO_PICKLE_PATH, 'wb') as cso_file:
            print("Creating ontology pickle file from a copy of the CSO Ontology found in",CSO_PATH)
            pickle.dump(cso, cso_file)
            

def check_model():
    """Function that checks if the model is available. If not, it will attempt to download it from a remote location.
    Tipically hosted on the CSO Portal.

    """
    
    if not os.path.exists(MODEL_PICKLE_PATH):
        print('[*] Beginning model download from', MODEL_PICKLE_REMOTE_URL)
        download_file(MODEL_PICKLE_REMOTE_URL, MODEL_PICKLE_PATH)  

def check_cached_model():
    """Function that checks if the cached model is available. If not, it will attempt to download it from a remote location.
    Tipically hosted on the CSO Portal.

    """
    
    if not os.path.exists(CACHED_MODEL):
        print('[*] Beginning download of cached model from', CACHED_MODEL_REMOTE_URL)
        download_file(CACHED_MODEL_REMOTE_URL, CACHED_MODEL) 
        
        
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
            #f.write(response.content)
            print('There was an error while downloading the new version of the ontology.')
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


def climb_ontology(cso, found_topics, climb_ont):
        """Function that climbs the ontology. This function might retrieve
            just the first broader topic or the whole branch up until root
        Args:
            found_topics (dictionary): It contains the topics found with string similarity.
            cso (dictionary): the ontology previously loaded from the file.
            num_narrower (integer): it defines the number of narrower topics before their broader topic gets included
            in the final set of topics. Default = 1.
            climb_ont (string): either "first" or "all" for selecting "just the first broader topic" or climbing
            the "whole tree".
        Returns:
            found_topics (dictionary): containing the found topics with their similarity and the n-gram analysed.
        """

        all_broaders = {}
        inferred_topics = {}
        num_narrower = 1

        if climb_ont == 'first':
            all_broaders = get_broader_of_topics(cso, found_topics, all_broaders)
        elif climb_ont == 'all':
            while True:
                """
                recursively adding new broaders based on the current list of topics. Broaders var increases each 
                iteration. It stops when it does not change anymore.
                """
                all_broaders_back = all_broaders.copy()
                all_broaders = get_broader_of_topics(cso, found_topics, all_broaders)
                if all_broaders_back == all_broaders:  # no more broaders have been found
                    break
        elif climb_ont == 'no':
            return inferred_topics #it is empty at this stage
        else:
            raise ValueError("Error: Field climb_ontology must be 'first', 'all' or 'no'")
            return
        
        
        for broader, narrower in all_broaders.items():
            if len(narrower) >= num_narrower:
                broader = get_primary_label(broader, cso['primary_labels'])
                if broader not in inferred_topics:
                    inferred_topics[broader] = [{'matched': len(narrower), 'broader of': narrower}]
                else:
                    inferred_topics[broader].append({'matched': len(narrower), 'broader of': narrower})

        return inferred_topics



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

    topics = list(found_topics) + list(all_broaders.keys())
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

def chunks(data, size):
    """Yield successive n-sized chunks from l."""
    
    # https://stackoverflow.com/questions/22878743/how-to-split-dictionary-into-multiple-dictionaries-fast
    it = iter(data)
    for i in range(0, len(data), size):
        yield {k:data[k] for k in islice(it, size)}

def get_network(cso, found_topics):
    """Function that extracts the network from a given set of topics.
    Args:
        found_topics (list): It contains the list of identified topics.
        cso (dictionary): the ontology previously loaded from the file.

    Returns:
        network (dictionary): = {"nodes":nodes, "edges":edges} contains the list of nodes and edges of the extracetd network.
    """
    
    if type(found_topics) is dict:
        list_of_topics = []
        for key, value in found_topics.items():
            list_of_topics += value
        
        list_of_topics = list(set(list_of_topics))
    elif type(found_topics) is list:
        list_of_topics = found_topics
        
    from collections import deque
    topics = []
    for topic in list_of_topics:
        if topic in cso["topics"]:
            topics.append(topic)
        else: 
            print("Asked to process '",topic,"', but I couldn't find it in the current version of the Ontology")

    nodes = []
    edges = []
    
    
    nodes.append({"id":"paper", "label":"paper"})
    t_id = 0
    pos = {}
    for topic in topics:
        pos[topic] = t_id
        pos[t_id] = topic
        temp={"id":"topic"+str(t_id), "label":topic}
        nodes.append(temp)
        t_id += 1
    
    
    matrix = np.ones((len(topics),len(topics)), dtype=int)*999
    queue = deque()
    for topic in topics:
        queue.append({"t":topic,"d":1})
        while len(queue) > 0:
            dequeued = queue.popleft()
            if dequeued["t"] in cso["broaders"]:
                broaders = cso["broaders"][dequeued["t"]]
                for broader in broaders:
                    if broader in pos:
                        matrix[pos[topic]][pos[broader]] = dequeued["d"]
                    queue.append({"t":broader,"d":dequeued["d"]+1})
    
    
    for topic in topics:
        nearest_min = matrix[pos[topic]].min()
        nearest_pos = np.where(matrix[pos[topic]] == nearest_min)[0]
        
        if(nearest_min == 1):
            for near in nearest_pos:
                edge = {"id":"edge","source":topic,"target":pos[near],"kind":"hard"}
                edges.append(edge)
        elif(nearest_min > 1 and nearest_min < 999):
            for near in nearest_pos:
                edge = {"id":"edge","source":topic,"target":pos[near],"kind":"soft"}
                edges.append(edge)
        else:
            edge = {"id":"edge","source":topic,"target":"paper","kind":"conn"}
            edges.append(edge)
        
        
    
    network = {"nodes":nodes, "edges":edges}
    return network


def plot_network(network):
    """Function that plots the network of topics.
        It mainly relies on networkx

    Args:
        network (dictionary): computed network.


    Returns:
        
        """
    
    G = nx.DiGraph()
    labels={}
    for node in network["nodes"]:
        G.add_node(node["label"])
        labels[node["label"]] = r'$'+node["label"]+'$'
        
        
    for edge in network["edges"]:
        G.add_edge(edge["source"],edge["target"],kind=edge["kind"])
        
      
        
    pos = nx.spring_layout(G)
    
    
        
    hard=[(u,v) for (u,v,d) in G.edges(data=True) if d['kind'] == "hard"]
    soft=[(u,v) for (u,v,d) in G.edges(data=True) if d['kind'] == "soft"]
    conn=[(u,v) for (u,v,d) in G.edges(data=True) if d['kind'] == "conn"]
    
    
    remain = [i for i in G.nodes() if i!="paper"]  
    nx.draw_networkx_nodes(G,pos, nodelist=["paper"], node_color='orange',node_shape = 's', node_size=500, alpha=1)
    nx.draw_networkx_nodes(G,pos, nodelist=remain, node_color='#167096',node_shape = 'o', node_size=100, alpha=1)
    
    
    
    nx.draw_networkx_edges(G,pos,edgelist=hard,width=1)
    nx.draw_networkx_edges(G,pos,edgelist=soft,width=1,alpha=0.5,style='dashed')
    nx.draw_networkx_edges(G,pos,edgelist=conn,width=1,edge_color='black')
    
    nx.draw_networkx_labels(G,pos,font_size=9,font_family='sans-serif')
    
    import matplotlib.pyplot as plt  
    plt.axis('off')
    plt.show()
    
    
    
def plot_network2(network):
    """Function that plots the network of topics.
        It mainly relies on webweb: https://github.com/dblarremore/webweb

    Args:
        network (dictionary): computed network.


    Returns:
        
        """
    
    G = nx.Graph()
    for node in network["nodes"]:
        G.add_node(node["label"])
        G.nodes[node["label"]]['isPaper'] = False
        
    G.nodes["paper"]['isPaper'] = True
        
        
    for edge in network["edges"]:
        G.add_edge(edge["source"],edge["target"],kind=edge["kind"],style='dashed')
        
        
    # create the web
    web = Web(nx_G=G)
    
    web.display.showNodeNames = True
    web.display.colorBy = 'isPaper'

    web.show()
    
def get_coverage(cso, found_topics):
    """Function that for a given topics, it returns its coverage.
    This coverage is computed based on how many its descendants have been identified.
    
    Args:
        found_topics (list): It contains the list of identified topics.
        cso (dictionary): the ontology previously loaded from the file.

    Returns:
        coverage (dictionary): = {"topic":percentage value} contains all found topics with their percentage of coverage.
    """
    
    coverage = {}
    
    if type(found_topics) is dict:
        list_of_topics = []
        for key, value in found_topics.items():
            list_of_topics += value
        
        list_of_topics = list(set(list_of_topics))
    elif type(found_topics) is list:
        list_of_topics = found_topics
        
    
    t_id = 0
    pos = {}     
    topics = []
    for topic in list_of_topics:
        if topic in cso["topics"]:
            topics.append(topic)
            pos[topic] = t_id
            pos[t_id] = topic
            t_id += 1
        else: 
            print("Asked to process '",topic,"', but I couldn't find it in the current version of the Ontology")
    
    matrix = np.zeros((len(topics),len(topics)), dtype=int)
    np.fill_diagonal(matrix, 1)
    
    from collections import deque
    queue = deque()
    for topic in topics:
        queue.append(topic)
        while len(queue) > 0:
            dequeued = queue.popleft()
            if dequeued in cso["broaders"]:
                broaders = cso["broaders"][dequeued]
                for broader in broaders:
                    if broader in pos:
                        matrix[pos[topic]][pos[broader]] = 1#dequeued["d"]
                    queue.append(broader)
    
    
    
    dividend = len(topics) #or np.sum(matrix)
    
    if(dividend > 0):
        general_coverage = np.sum(matrix,axis=0)
        
        for topic in topics:
            coverage[topic] = round(general_coverage[pos[topic]]/dividend,3)
    else:
        print("I was about to perform a divide by zero operation")
        
    return coverage
    
