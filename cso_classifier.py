#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 23 15:16:13 2018

@author: angelosalatino
"""
import csv
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk import ngrams
from nltk.tokenize import word_tokenize
import Levenshtein.StringMatcher as ls


def load_cso(file):
    """Function that loads the CSO from the file in a dictionary.
       In particular, it load all the relationships organised in boxes:
           - topics, the list of topics
           - broaders, the list of broaders for a given topic
           - same_as, all the siblings for a given topic

    Args:
        file (string): The path of the file constaining the ontology.

    Returns:
        cso (dictionary): {'topics':topics, 'broaders':broaders, 'same_as':same_as}.


    """
    with open(file) as ontoFile:
        topics = {}
        broaders = {}
        same_as = {}
        ontology = csv.reader(ontoFile, delimiter=';')
        for triple in ontology:
            if triple[1] == 'klink:broaderGeneric':
                if triple[2] in broaders:
                    broaders[triple[2]].append(triple[0])
                else:
                    broaders[triple[2]] = [triple[0]]
            elif triple[1] == 'klink:relatedEquivalent':
                if triple[2] in same_as:
                    same_as[triple[2]].append(triple[0])
                else:
                    same_as[triple[2]] = [triple[0]]
            elif triple[1] == 'rdfs:label':
                topics[triple[0]] = True

    cso = {'topics':topics, 'broaders':broaders, 'same_as':same_as}

    return(cso)


def cso_classifier(paper, cso, format="text", num_narrower=2, min_similarity=0.85, climb_ont='jfb', verbose=False):
    """Function that classifies a single paper. If you have a collection of papers, 
        you must call this function for each paper and organise the result.
       Initially, it cleans the paper file, removing stopwords (English ones) and punctuation.
       Then it extracts n-grams (1,2,3) and with a Levenshtein it check the similarity for each of
       them with the topics in the ontology.
       Next, it climbs the ontology, by selecting either the first broader topic or the whole set of
       broader topics until root is reached.

    Args:
        paper (either string or dictionary): The paper to analyse. It can be a full string in which the content
        is already merged or a dictionary  {"title": "","abstract": "","keywords": ""}.
        cso (dictionary): the ontology previously loaded from the file.
        format (string): either "text" or "json" to determine wether the paper is either in a string or dictionary respectively. Default = "text".
        num_narrower (integer): it defines the number of narrower topics before their broader topic gets included in the final set of topics. Default = 2.
        min_similarity (integer): minimum Levenshtein similarity between the n-gram and the topics within the CSO. Default = 0.85.
        climb_ont (string): either "jfb" or "wt" for selecting "just the first broader topic" or climbing the "whole tree".
        verbose (bool): True or False, whether the result should contain also statistical values for matchings. Useful for debugging. Default False.

    Returns:
        found_topics (dictionary): containing the found topics with their similarity and the n-gram analysed.
    """

    if format == 'json':
        t_paper = paper
        paper = ""
        for key in list(t_paper.keys()):
            paper = paper + t_paper[key] + " "
    elif format == 'text':
        pass #do nothing
    else:
        print("Error: Field format must be either 'json' or 'text'")
        return

    # preprocessing
    paper = paper.lower()
    tokenizer = RegexpTokenizer(r'[\w\-\(\)]*')
    tokens = tokenizer.tokenize(paper)
    filtered_words = [w for w in tokens if not w in stopwords.words('english')]
    paper = " ".join(filtered_words)


    # analysing similarity with terms in the ontology
    found_topics = statistic_similarity(paper, cso, min_similarity)

    # extract more concepts from the ontology
    found_topics = climb_ontology(found_topics, cso, num_narrower=num_narrower, climb_ont=climb_ont)

    if verbose is False:
        found_topics = strip_explanation(found_topics, cso)

    return found_topics



def statistic_similarity(paper, cso, min_similarity):
    """Function that splits the paper text in n-grams (unigrams,bigrams,trigrams)
    and with a Levenshtein it check the similarity for each of them with the topics in the ontology.

    Args:
        paper (string): The paper to analyse. At this stage it is a string.
        cso (dictionary): the ontology previously loaded from the file.
        min_similarity (integer): minimum Levenshtein similarity between the n-gram and the topics within the CSO. 

    Returns:
        found_topics (dictionary): containing the found topics with their similarity and the n-gram analysed.
    """

    # analysing grams
    found_topics = {}

    unigrams = ngrams(word_tokenize(paper, preserve_line=True), 1)
    for grams in unigrams:
        gram = " ".join(grams)
        topics = [key for key, _ in cso['topics'].items() if key.startswith(gram[:4])]
        for topic in topics:
            m = ls.StringMatcher(None, topic, gram).ratio()
            if m >= min_similarity:
                if topic in found_topics:
                    found_topics[topic].append({'matched':gram, 'similarity':m})
                else:
                    found_topics[topic] = [{'matched':gram, 'similarity':m}]

    bigrams = ngrams(word_tokenize(paper, preserve_line=True), 2)
    for grams in bigrams:
        gram = " ".join(grams)
        topics = [key for key, _ in cso['topics'].items() if key.startswith(gram[:4])]
        for topic in topics:
            m = ls.StringMatcher(None, topic, gram).ratio()
            if m >= min_similarity:
                if topic in found_topics:
                    found_topics[topic].append({'matched':gram, 'similarity':m})
                else:
                    found_topics[topic] = [{'matched':gram, 'similarity':m}]

    trigrams = ngrams(word_tokenize(paper, preserve_line=True), 3)
    for grams in trigrams:
        gram = " ".join(grams)
        topics = [key for key, _ in cso['topics'].items() if key.startswith(gram[:4])]
        for topic in topics:
            m = ls.StringMatcher(None, topic, gram).ratio()
            if m >= min_similarity:
                if topic in found_topics:
                    found_topics[topic].append({'matched':gram, 'similarity':m})
                else:
                    found_topics[topic] = [{'matched':gram, 'similarity':m}]

    return found_topics



def climb_ontology(found_topics,cso,num_narrower,climb_ont):
    """Function that climbs the ontology. This function might retrieve
        just the first broader topic or the whole branch up until root

    Args:
        found_topics (dictionary): It contains the topics found with string similarity.
        cso (dictionary): the ontology previously loaded from the file.
        num_narrower (integer): it defines the number of narrower topics before their broader topic gets included in the final set of topics. Default = 2.
        climb_ont (string): either "jfb" or "wt" for selecting "just the first broader topic" or climbing the "whole tree".

    Returns:
        found_topics (dictionary): containing the found topics with their similarity and the n-gram analysed.
    """

    all_broaders = {}

    if climb_ont == 'jfb':
        all_broaders = get_broader_of_topics(found_topics,all_broaders,cso)
    elif climb_ont == 'wt':
        while True: #recursively adding new broaders based on the current list of topics. Broaders var increases each iteration. It stops when it does not change anymore.
            all_broaders_back = all_broaders.copy()
            all_broaders = get_broader_of_topics(found_topics, all_broaders, cso)
            if all_broaders_back == all_broaders: # no more broaders have been found
                break
    elif climb_ont == 'no':
        return found_topics
    else:
        print("Error: Field climb_ontology must be 'jfb', 'wt' or 'no'")
        return


    for broader, narrower in all_broaders.items():    
        if len(narrower) >= num_narrower:
            if broader not in found_topics:
                found_topics[broader] = [{'matched':len(narrower), 'broader of':narrower}]
            else:
                found_topics[broader].append({'matched':len(narrower), 'broader of':narrower})
        
            
    return found_topics


def get_broader_of_topics(found_topics,all_broaders,cso):
    """Function that returns all the broader topics for a given set of topics.
        It analyses the broader topics of both the topics initially found in the paper, and the broader topics found at the previous iteration.
        It incrementally provides a more comprehensive set of broader topics.

    Args:
        found_topics (dictionary): It contains the topics found with string similarity.
        all_broaders (dictionary): It contains the broader topics found in the previous run. Otherwise an empty object.
        cso (dictionary): the ontology previously loaded from the file.

    Returns:
        all_broaders (dictionary): contains all the broaders found so far, including the previous iterations.
    """

    topics = list(found_topics.keys()) + list(all_broaders.keys())
    for topic in topics:
        if topic in cso['broaders']:
            broaders = cso['broaders'][topic]
            for broader in broaders:
                if broader in all_broaders:
                    if topic not in all_broaders[broader]:
                        all_broaders[broader].append(topic)
                    else:
                        pass # the topic was listed before
                else:
                    all_broaders[broader] = [topic]

    return all_broaders


def strip_explanation(found_topics, cso):
    """Function that removes statistical values from the dictionary containing the found topics.
        It returns only the topics. It removes the same as, picking the longest string in alphabetical order.

    Args:
        found_topics (dictionary): It contains the topics found with string similarity.
        cso (dictionary): the ontology previously loaded from the file.

    Returns:
        topic (array): array containing the list of topics.
    """

    topics = list(found_topics.keys()) #takes only the keys
    topics = remove_same_as(topics, cso) #unifies the same_As
    topics = list(set(topics)) #finds unique topics
    return topics

def remove_same_as(topics,cso):
    """Function that removes the same as, picking the longest string in alphabetical order.

    Args:
        topics (array): It contains the list of topics found with the classifier, without statistics.
        cso (dictionary): the ontology previously loaded from the file.

    Returns:
        final_topics (array): the filtered topics without their siblings.
    """

    final_topics = []
    for topic in topics:
        if topic in cso['same_as']:
            # Let's take all the same-as
            same_as = cso['same_as'][topic].copy()
            same_as.append(topic)
            # sort them alphabetically
            same_as = sorted(same_as)
            # append the first longest topic
            final_topics.append(max(same_as, key=len))
        else:
            final_topics.append(topic)

    return final_topics
