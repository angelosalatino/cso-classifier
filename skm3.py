#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Computer Science Ontology API 2018

@author: angelosalatino
"""
import csv
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk import ngrams
from nltk.tokenize import word_tokenize
import Levenshtein.StringMatcher as ls


class CSOClassifier:
    """ An simple abstraction layer for using CSO classifier """

    def __init__(self, version=2):
        
        self.version = version
        
        if version == 1:
            self.filename = 'ontology/ComputerScienceOntology.csv'
        elif version == 2:
            self.filename = 'ontology/ComputerScienceOntology_v2.csv'
        else:
            raise ValueError(f"Could not recognise value: {version}. Please specify version 1 or 2.")
            exit(0)

        # Initialise variables to store CSO data - loads into memory 
        self.cso = {}

    def load_cso(self):
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

        with open(self.filename, 'r') as ontoFile:
            topics = {}
            broaders = {}
            narrowers = {}
            same_as = {}
            primary_labels = {}
            ontology = csv.reader(ontoFile, delimiter=';')

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
                elif triple[1] == 'klink:primaryLabel':
                    primary_labels[triple[0]] = triple[2]

        self.cso = {
            'topics': topics,
            'broaders': broaders,
            'narrowers': narrowers,
            'same_as': same_as,
            'primary_labels': primary_labels
        }

    def load_cso_branch(self, seed='semantic web'):
        """Function that loads a portion of the CSO, starting from a seed topic.
           In particular, it load all the relationships organised in boxes:
               - topics, the list of topics
               - broaders, the list of broader topics for a given topic
               - narrowers, the list of narrower topics for a given topic
               - same_as, all the siblings for a given topic
               - primary_labels, the primary label of a topic, if it belongs to a cluster

        Args:
            file (string): The path of the file constaining the ontology.
            seed (string): Root topic from which extract the portion of ontology

        Returns:
            cso (dictionary): {'topics':topics, 'broaders':broaders, 'narrowers':narrowers, 'same_as':same_as, 'primary_labels': primary_labels}.

        """

        full_cso = self.load_cso(self.filename)

        relationships = full_cso['narrowers']
        list_of_topics = full_cso['topics']

        if seed not in list_of_topics:
            print("Error: " + seed + " not found in CSO")
            return False

        sub_seed_topics = dict()
        sub_seed_topics[seed] = True

        queue = [seed]
        while len(queue) > 0:
            t_topic = queue.pop(0)
            if t_topic in relationships:
                for topic in relationships[t_topic]:
                    queue.append(topic)
                    sub_seed_topics[topic] = True

        # let's extract the portion of ontology
        with open(self.filename) as ontoFile:
            topics = {}
            broaders = {}
            narrowers = {}
            same_as = {}
            primary_labels = {}
            ontology = csv.reader(ontoFile, delimiter=';')

            for triple in ontology:
                if triple[0] in sub_seed_topics:
                    if triple[1] == 'klink:broaderGeneric':
                        if triple[2] in sub_seed_topics:
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
                    elif triple[1] == 'klink:primaryLabel':
                        primary_labels[triple[0]] = triple[2]

        self.cso = {
            'topics': topics,
            'broaders': broaders,
            'narrowers': narrowers,
            'same_as': same_as,
            'primary_labels': primary_labels
        }

    def classify(self, paper, num_narrower=2, min_similarity=0.85, climb_ont='jfb', verbose=False):
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
            format (string): either "text" or "json" to determine wether the paper is either in a string or
            dictionary respectively. Default = "text".
            num_narrower (integer): it defines the number of narrower topics before their broader topic gets
            included in the final set of topics. Default = 2.
            min_similarity (integer): minimum Levenshtein similarity between the n-gram and the topics within
            the CSO. Default = 0.85.
            climb_ont (string): either "jfb" or "wt" for selecting "just the first broader topic" or climbing the
            "whole tree".
            verbose (bool): True or False, whether the result should contain also statistical values for matchings.
            Useful for debugging. Default False.

        Returns:
            found_topics (dictionary): containing the found topics with their similarity and the n-gram analysed.
        """

        if isinstance(paper, dict):
            t_paper = paper
            paper = ""
            for key in list(t_paper.keys()):
                paper = paper + t_paper[key] + " "
        elif isinstance(paper, str):
            pass
        else:
            raise TypeError("Error: Field format must be either 'json' or 'text'")
            return

        # pre-processing
        paper = paper.lower()
        tokenizer = RegexpTokenizer(r'[\w\-\(\)]*')
        tokens = tokenizer.tokenize(paper)
        filtered_words = [w for w in tokens if w not in stopwords.words('english')]
        paper = " ".join(filtered_words)

        # analysing similarity with terms in the ontology
        extracted_topics = self.statistic_similarity(paper, min_similarity)

        # extract more concepts from the ontology
        inferred_topics = self.climb_ontology(extracted_topics, num_narrower=num_narrower, climb_ont=climb_ont)
        
        topics = {'extracted': extracted_topics, 'inferred': inferred_topics}

        if verbose is False:
            topics = self.strip_explanation(topics)

        return topics

    def statistic_similarity(self, paper, min_similarity):
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
        
        idx = 0
        trigrams = ngrams(word_tokenize(paper, preserve_line=True), 3)
        matched_trigrams = []
        for grams in trigrams:
            idx += 1
            gram = " ".join(grams)
            topics = [key for key, _ in self.cso['topics'].items() if key.startswith(gram[:4])]
            for topic in topics:
                m = ls.StringMatcher(None, topic, gram).ratio()
                if m >= min_similarity:
                    topic = self.get_primary_label(topic, self.cso['primary_labels'])
                    if topic in found_topics:
                        found_topics[topic].append({'matched': gram, 'similarity': m})
                    else:
                        found_topics[topic] = [{'matched': gram, 'similarity': m}]
                    matched_trigrams.append(idx)
            
        
        idx = 0
        bigrams = ngrams(word_tokenize(paper, preserve_line=True), 2)
        matched_bigrams = []
        for grams in bigrams:
            idx += 1
            if (idx not in matched_trigrams) and ((idx-1) not in matched_trigrams):
                gram = " ".join(grams)
                topics = [key for key, _ in self.cso['topics'].items() if key.startswith(gram[:4])]
                for topic in topics:
                    m = ls.StringMatcher(None, topic, gram).ratio()
                    if m >= min_similarity:
                        topic = self.get_primary_label(topic, self.cso['primary_labels'])
                        if topic in found_topics:
                            found_topics[topic].append({'matched': gram, 'similarity': m})
                        else:
                            found_topics[topic] = [{'matched': gram, 'similarity': m}]
                        matched_bigrams.append(idx)
            

        idx = 0
        unigrams = ngrams(word_tokenize(paper, preserve_line=True), 1)
        for grams in unigrams:
            idx += 1
            if (idx not in matched_trigrams) and ((idx-1) not in matched_trigrams) and (idx not in matched_bigrams) and ((idx-1) not in matched_bigrams) and ((idx-1) not in matched_bigrams):
                gram = " ".join(grams)
                if gram == "semantic":
                    print("I am here")
                topics = [key for key, _ in self.cso['topics'].items() if key.startswith(gram[:4])]
                for topic in topics:
                    m = ls.StringMatcher(None, topic, gram).ratio()
                    if m >= min_similarity:
                        topic = self.get_primary_label(topic, self.cso['primary_labels'])
                        if topic in found_topics:
                            found_topics[topic].append({'matched': gram, 'similarity': m})
                        else:
                            found_topics[topic] = [{'matched': gram, 'similarity': m}]
            

        return found_topics

    def climb_ontology(self, found_topics, num_narrower, climb_ont):
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

        if climb_ont == 'jfb':
            all_broaders = self.get_broader_of_topics(found_topics, all_broaders)
        elif climb_ont == 'wt':
            while True:
                """
                recursively adding new broaders based on the current list of topics. Broaders var increases each 
                iteration. It stops when it does not change anymore.
                """
                all_broaders_back = all_broaders.copy()
                all_broaders = self.get_broader_of_topics(found_topics, all_broaders)
                if all_broaders_back == all_broaders:  # no more broaders have been found
                    break
        elif climb_ont == 'no':
            return inferred_topics #it is empty at this stage
        else:
            raise ValueError("Error: Field climb_ontology must be 'jfb', 'wt' or 'no'")
            return
        
        
        for broader, narrower in all_broaders.items():
            if len(narrower) >= num_narrower:
                broader = self.get_primary_label(broader, self.cso['primary_labels'])
                if broader not in inferred_topics:
                    inferred_topics[broader] = [{'matched': len(narrower), 'broader of': narrower}]
                else:
                    inferred_topics[broader].append({'matched': len(narrower), 'broader of': narrower})

        return inferred_topics
    

    def get_broader_of_topics(self, found_topics, all_broaders):
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

        topics = list(found_topics.keys()) + list(all_broaders.keys())
        for topic in topics:
            if topic in self.cso['broaders']:
                broaders = self.cso['broaders'][topic]
                for broader in broaders:
                    if broader in all_broaders:
                        if topic not in all_broaders[broader]:
                            all_broaders[broader].append(topic)
                        else:
                            pass  # the topic was listed before
                    else:
                        all_broaders[broader] = [topic]

        return all_broaders

    def strip_explanation(self, found_topics):
        """Function that removes statistical values from the dictionary containing the found topics.
            It returns only the topics. It removes the same as, picking the longest string in alphabetical order.

        Args:
            found_topics (dictionary): It contains the topics found with string similarity.
            cso (dictionary): the ontology previously loaded from the file.

        Returns:
            topic (array): array containing the list of topics.
        """
        
        
        extracted_topics = set(found_topics['extracted'].keys())  # Takes only the keys
        inferred_topics = set(found_topics['inferred'].keys()).difference(extracted_topics) #removes the inferred topics that are also extracted
        if (self.version == 1):
            extracted_topics = set(self.remove_same_as(extracted_topics))
            inferred_topics  = set(self.remove_same_as(inferred_topics))
            
        topics = {'extracted': list(extracted_topics), 'inferred': list(inferred_topics)}
        return topics
    

    def remove_same_as(self, topics):
        """Function that removes the same as, picking the longest string in alphabetical order.
            This function is obsolete. It is still here for legacy purposes (in case we run the classifier
            with the version 1 of the ontology).
            
        Args:
            topics (array): It contains the list of topics found with the classifier, without statistics.
            cso (dictionary): the ontology previously loaded from the file.
        Returns:
            final_topics (array): the filtered topics without their siblings.
        """

        final_topics = []
        for topic in topics:
            if topic in self.cso['same_as']:
                # Let's take all the same-as
                same_as = self.cso['same_as'][topic].copy()
                same_as.append(topic)
                # sort them alphabetically
                same_as = sorted(same_as)
                # append the first longest topic
                final_topics.append(max(same_as, key=len))
            else:
                final_topics.append(topic)

        return final_topics

    def retrieve_narrower_topics(self, seed, depth='wt'):
        """Function that retrieves the narrower topics of a given seed topic.

        Args:
            seed (string): seed topic from which selecting its narrower topics
            cso (dictionary): the ontology previously loaded from the file.
            depth (string): either "jfn" or "wt" for selecting "just the first narrower topics" or selecting all the
            topics in the "whole sub-tree".

        Returns:
            topics (array): the unique topics selected from the seed. Or False in case the topic does not exist
            in the ontology.
        """

        list_of_topics = self.cso['topics']

        if seed not in list_of_topics:
            print("Error: " + seed + " not found in CSO")
            return False

        relationships = self.cso['narrowers']

        topics = {}

        if seed not in relationships:
            print("Error: No narrower topics found for " + seed)
            return list(topics.keys())

        # topics[seed] = True

        if depth == 'wt':
            queue = [seed]
            while len(queue) > 0:
                t_topic = queue.pop(0)
                if t_topic in relationships:
                    for topic in relationships[t_topic]:
                        queue.append(topic)
                        topics[topic] = True
        elif depth == 'jfn':
            for topic in relationships[seed]:
                topics[topic] = True
        else:
            print("Error: Field climb_ontology must be either 'jfn' or 'wt'")
            return

        return list(topics.keys())


    def get_primary_label(self, topic, primary_labels):
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