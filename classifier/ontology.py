import pickle
import os
import csv as co

from classifier.config import Config
from classifier import misc


class Ontology:
    """ A simple abstraction layer for using the Computer Science Ontology """
    
    def __init__(self):
        """ Initialising the ontology class
        """
        self.topics = dict()
        self.topics_wu = dict()
        self.broaders = dict()
        self.narrowers = dict()
        self.same_as = dict()
        self.primary_labels = dict()
        self.primary_labels_wu = dict()
        self.topic_stems = dict()
        
        self.config = Config()
        
        self.ontology_attr = ('topics', 'topics_wu', 'broaders', 'narrowers', 'same_as', 'primary_labels', 'primary_labels_wu', 'topic_stems')
        
        self.load_ontology_pickle()
        
        

    def load_cso_from_csv(self):
        """Function that loads the CSO from the file in a dictionary.
           In particular, it load all the relationships organised in boxes:
               - topics, the list of topics
               - broaders, the list of broader topics for a given topic
               - narrowers, the list of narrower topics for a given topic
               - same_as, all the siblings for a given topic
               - primary_labels, all the primary labels of topics, if they belong to clusters
               - topics_wu, topic with underscores
               - primary_labels_wu, primary labels with underscores
        """
    
        with open(self.config.get_cso_path(), 'r') as ontoFile:

            ontology = co.reader(ontoFile, delimiter=';')
    
            for triple in ontology:
                if triple[1] == 'klink:broaderGeneric':
                    # loading broader topics
                    if triple[2] in self.broaders:
                        self.broaders[triple[2]].append(triple[0])
                    else:
                        self.broaders[triple[2]] = [triple[0]]
    
                    # loading narrower topics
                    if triple[0] in self.narrowers:
                        self.narrowers[triple[0]].append(triple[2])
                    else:
                        self.narrowers[triple[0]] = [triple[2]]
                elif triple[1] == 'klink:relatedEquivalent':
                    if triple[2] in self.same_as:
                        self.same_as[triple[2]].append(triple[0])
                    else:
                        self.same_as[triple[2]] = [triple[0]]
                elif triple[1] == 'rdfs:label':
                    self.topics[triple[0]] = True
                    self.topics_wu[triple[0].replace(" ", "_")] = triple[0]
                elif triple[1] == 'klink:primaryLabel':
                    self.primary_labels[triple[0]] = triple[2]
                    self.primary_labels_wu[triple[0].replace(" ", "_")] = triple[2].replace(" ", "_")
            

            for topic in self.topics.keys():
                if topic[:4] not in self.topic_stems:
                    self.topic_stems[topic[:4]] = list()
                self.topic_stems[topic[:4]].append(topic)
            
    
        
    def from_single_items_to_cso(self):
        return {attr: getattr(self, attr) for attr in self.ontology_attr}
    
    def from_cso_to_single_items(self, cso):
        for attr in self.ontology_attr:
            setattr(self, attr, cso[attr])
    

    def load_ontology_pickle(self):
        """Function that loads CSO. 
        This file has been serialised using Pickle allowing to be loaded quickly.
        """
        self.check_ontology()
        ontology = pickle.load(open(self.config.get_cso_pickle_path(), "rb" ))
        self.from_cso_to_single_items(ontology)
        print("Computer Science Ontology loaded.")


     
    def check_ontology(self):
        """Function that checks if the ontology is available. 
        If not, it will check if a csv version exists and then it will create the pickle file.
        """ 
        
        if not os.path.exists(self.config.get_cso_pickle_path()):
            print("Ontology pickle file is missing.")
            
            if not os.path.exists(self.config.get_cso_path()):
                print("The source file of the Computer Science Ontology is missing. Attempting to download it now...")
                misc.download_file(self.config.get_cso_remote_url(), self.config.get_cso_path()) 
            
            self.load_cso_from_csv()

            with open(self.config.get_cso_pickle_path(), 'wb') as cso_file:
                print("Creating ontology pickle file from a copy of the CSO Ontology found in",self.config.get_cso_path())
                pickle.dump(self.from_single_items_to_cso(), cso_file)
                



    def get_primary_label(self, topic):
        """Function that returns the primary (preferred) label for a topic. If this topic belongs to 
        a cluster.

        Args:
            topic (string): Topic to analyse.
            primary_labels (dictionary): It contains the primary labels of all the topics belonging to clusters.

        Returns:
            topic (string): primary label of the analysed topic.
        """
        
        try:
            topic = self.primary_labels[topic]
        except KeyError:
            pass
        
        return topic
    
    
    def get_primary_label_wu(self, topic):
        """Function that returns the primary (preferred) label for a topic with underscore. If this topic belongs to 
        a cluster.

        Args:
            topic (string): Topic to analyse.
            primary_labels (dictionary): It contains the primary labels of all the topics belonging to clusters.

        Returns:
            topic (string): primary label of the analysed topic with underscore.
        """
        
        try:
            topic = self.primary_labels_wu[topic]
        except KeyError:
            pass
        
        return topic


    def climb_ontology(self, found_topics, climb_ont):
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
            all_broaders = self.get_broader_of_topics(found_topics, all_broaders)
        elif climb_ont == 'all':
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
            raise ValueError("Error: Field climb_ontology must be 'first', 'all' or 'no'")
            return
        
        
        for broader, narrower in all_broaders.items():
            if len(narrower) >= num_narrower:
                broader = self.get_primary_label(broader)
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
    
        topics = list(found_topics) + list(all_broaders.keys())
        for topic in topics:
            if topic in self.broaders:
                broaders = self.broaders[topic]
                for broader in broaders:
                    if broader in all_broaders:
                        if topic not in all_broaders[broader]:
                            all_broaders[broader].append(topic)
                        else:
                            pass  # the topic was listed before
                    else:
                        all_broaders[broader] = [topic]
    
        return all_broaders
