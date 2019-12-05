import pickle
import os
import sys
import requests
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

    fcso = pickle.load(open(CSO_PICKLE_PATH, "rb"))
    fmodel = pickle.load(open(MODEL_PICKLE_PATH, "rb"))
    
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
       fmodel = json.load(f)
    
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