import pickle
import os
import csv as co

from classifier.config import Config
from classifier import misc


class Ontology:
    """ A simple abstraction layer for using the Computer Science Ontology """
    
    def __init__(self, load_ontology = True):
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
        
        if load_ontology:
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
               - topic_stems, groups together topics that start with the same 4 letters
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
            
            with open(self.config.get_cso_pickle_path(), 'wb') as cso_file:
                print("Creating ontology pickle file from a copy of the CSO Ontology found in",self.config.get_cso_path())
                pickle.dump(self.from_single_items_to_cso(), cso_file)

    
        
    def from_single_items_to_cso(self):
        """ Function that returns a single dictionary containing all relevant values for the ontology.
        """
        return {attr: getattr(self, attr) for attr in self.ontology_attr}
    
    def from_cso_to_single_items(self, cso):
        """ Function that fills all the single relevant variables in this class.
        """
        for attr in self.ontology_attr:
            setattr(self, attr, cso[attr])
    

    def load_ontology_pickle(self):
        """ Function that loads CSO. 
        This file has been serialised using Pickle allowing to be loaded quickly.
        """
        self.check_ontology()
        ontology = pickle.load(open(self.config.get_cso_pickle_path(), "rb" ))
        self.from_cso_to_single_items(ontology)
        print("Computer Science Ontology loaded.")
            

    def get_primary_label(self, topic):
        """ Function that returns the primary (preferred) label for a topic. If this topic belongs to 
        a cluster.

        Args:
            topic (string): Topic to analyse.

        Returns:
            topic (string): primary label of the analysed topic.
        """
        
        try:
            topic = self.primary_labels[topic]
        except KeyError:
            pass
        
        return topic
    
    
    def get_primary_label_wu(self, topic):
        """ Function that returns the primary (preferred) label for a topic *with underscore*. If this topic belongs to 
        a cluster.

        Args:
            topic (string): Topic to analyse.

        Returns:
            topic (string): primary label of the analysed topic with underscore.
        """
        
        try:
            topic = self.primary_labels_wu[topic]
        except KeyError:
            pass
        
        return topic
    
    
    def get_topic_wu(self, topic):
        """ Function that returns the topic label (without underscore) from its underscored version.

        Args:
            topic (string): Topic to analyse.

        Returns:
            topic (string): primary label of the analysed topic with underscore.
        """
        
        try:
            topic = self.topics_wu[topic]
        except KeyError:
            pass
        
        return topic


    def climb_ontology(self, found_topics, climb_ont):
        """ Function that climbs the ontology. This function might retrieve
            just the first broader topic or the whole branch up until root
        Args:
            found_topics (list): It contains the topics found with string similarity.
            climb_ont (string): either "first" or "all" for selecting "just the first broader topic" or climbing
            the "whole tree".
        Returns:
            found_topics (dictionary): containing the found topics with their similarity and the n-gram analysed.
        """

        all_broaders = dict()
        num_narrowers = 1

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
            return dict() #it is empty at this stage
        else:
            raise ValueError("Error: Field climb_ontology must be 'first', 'all' or 'no'")
            return
        
        
        inferred_topics = dict()
        for broader, narrowers in all_broaders.items():
            if len(narrowers) >= num_narrowers:
                broader = self.get_primary_label(broader)
                if broader not in inferred_topics:
                    inferred_topics[broader] = {'matched': len(narrowers), 'broader of': list(narrowers)}
                else: # this branch folds when we have same as
                    this_broader_narrowers = set(inferred_topics[broader]['broader of'])
                    this_broader_narrowers = this_broader_narrowers.union(narrowers)
                    inferred_topics[broader] = {'matched': len(this_broader_narrowers), 'broader of': list(this_broader_narrowers)}
                    
        return inferred_topics


    def get_broader_of_topics(self, found_topics, all_broaders={}):
        """ Function that returns all the broader topics for a given set of topics.
            It analyses the broader topics of both the topics initially found in the paper, and the broader topics
            found at the previous iteration.
            It incrementally provides a more comprehensive set of broader topics.
    
        Args:
            found_topics (list): It contains the topics found with string similarity.
            all_broaders (dictionary): It contains the broader topics found in the previous run. Otherwise an empty object.
   
        Returns:
            all_broaders (dictionary): contains all the broaders found so far, including the previous iterations.
        """
        topics = list(found_topics) + list(all_broaders.keys())
        for topic in topics:
            try:
                broaders = self.broaders[topic]
                for broader in broaders:
                    if broader not in all_broaders:
                        all_broaders[broader] = set()
                    all_broaders[broader].add(topic)
                    if topic in all_broaders:
                        all_broaders[broader] = all_broaders[broader].union(all_broaders[topic])

            except KeyError:
                pass
            
        return all_broaders

    
    def check_ontology(self):
        """ Function that checks if the ontology is available. 
        If not, it will check if a csv version exists and then it will create the pickle file.
        """         
        if not os.path.exists(self.config.get_cso_pickle_path()):
            print("Ontology pickle file is missing.")
            
            if not os.path.exists(self.config.get_cso_path()):
                print("The source file of the Computer Science Ontology is missing. Attempting to download it now...")
                self.download_ontology() 
            
            self.load_cso_from_csv()
    
    
    def download_ontology(self):
        """ Function that allows to download the latest version of the ontology.
            If older versions of the ontology (both csv and pickle) are available they will be deleted.
        """
        try:
            os.remove(self.config.get_cso_pickle_path())
        except FileNotFoundError:
            pass
        
        try:
            os.remove(self.config.get_cso_path())
        except FileNotFoundError:
            pass
        
        ontology_remote_url, last_version = self.retrieve_url_of_latest_version_available()
        print("Downloading the Computer Science Ontology from {}".format(ontology_remote_url))
        task_completed = misc.download_file(ontology_remote_url, self.config.get_cso_path())
        self.config.set_cso_version(last_version)
        return task_completed
    
    
    def update(self, force = False):
        """ This funciton updates the ontology.
        
        Args:
            force (boolean): If false, it checks if a newer version is available. If false, it will delete all files and download the most recent version.
        """
        misc.print_header("ONTOLOGY")
        if force:
            print("Updating the ontology file")
            self.download_ontology() 
            self.load_cso_from_csv()

        else:
            last_version = self.retrieve_latest_version_available()
            if last_version > self.config.get_ontology_version():
                print("Updating the ontology file")
                self.download_ontology() 
                self.load_cso_from_csv()
            else:
                print("The ontology is already up to date.")
                
        
    def setup(self):
        """ Function that sets up the ontology. 
        """ 
        misc.print_header("ONTOLOGY")
        
        if not os.path.exists(self.config.get_cso_pickle_path()):
            
            if not os.path.exists(self.config.get_cso_path()):
                
                task_completed = self.download_ontology() 
                
                if task_completed:
                    print("Ontology file downloaded successfully.")
                else:
                    print("We were unable to complete the download of the ontology.")
            
            self.load_cso_from_csv()
            
            if os.path.exists(self.config.get_cso_pickle_path()):
                print("Ontology file created successfully.")
            
        else:
            print("Nothing to do. The ontology file is already available.")

                    
    def retrieve_url_of_latest_version_available(self):
        """ Function that retireves the version number of the latest ontology. 
        """
        version = self.retrieve_latest_version_available()
        composite_url = "{}/version-{}/cso_v{}.csv".format(self.config.get_cso_remote_url(),version,version)
        import urllib.request, json  
        with urllib.request.urlopen(self.config.get_cso_version_logger_url()) as url:
            data = json.loads(url.read().decode())
            if "last_version" in data and "url" in data['last_version']:
                return data['last_version']["url"], version
            else:
                return composite_url, version
        return composite_url, version
    
    
    def retrieve_latest_version_available(self):
        """ Function that retireves the version number of the latest ontology. 
        """
        import urllib.request, json  
        with urllib.request.urlopen(self.config.get_cso_version_logger_url()) as url:
            data = json.loads(url.read().decode())
            if "last_version" in data and "version" in data['last_version']:
                return data['last_version']["version"]
            else:
                return "0.0"
        return "0.0"
    
    
    def version(self):
        """ Function that returns the current version of the ontology available in this classifier
            It also checks whether there is a more up-to-date version.
        """
        misc.print_header("ONTOLOGY")
        print("CSO ontology version {}".format(self.config.get_ontology_version()))
        
        last_version = self.retrieve_latest_version_available()

        if last_version > self.config.get_ontology_version():
            print("A more recent version ({}) of the Computer Science Ontology is available.".format(last_version))
            print("You can update this package by running the following instructions:")
            print("1) import classifier.classifier as classifier")
            print("2) classifier.update()")
        elif last_version == self.config.get_ontology_version():
            print("The version of the CSO Ontology you are using is already up to date.") 
        elif last_version < self.config.get_ontology_version():
            print("Something is not right. The version you are using ({}) is ahead compared to the latest available ({}).".format(self.config.get_ontology_version(),last_version))
        
