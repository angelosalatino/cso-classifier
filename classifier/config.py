import configparser
import os



class Config:
    """ A simple abstraction layer for the configuration file """
     
    def __init__(self, paper = None):
        """ Initialising the config class
        """
        self.dir = os.path.dirname(os.path.realpath(__file__))
        self.config_file = os.path.join(self.dir, "config.ini")
        self.config = configparser.ConfigParser()
        self.read_config_file()
    
# =============================================================================
#     CLASSIFIER
# =============================================================================
    def get_classifier_version(self):
        return self.config['Classifier']['CLASSIFIER_VERSION']
    
    def set_classifier_version(self, version):
        self.config['Classifier']['CLASSIFIER_VERSION'] = version
        self.write_config_file()

# =============================================================================
#     ONTOLOGY
# =============================================================================
    def get_cso_path(self):
        return os.path.join(self.dir, self.config['Ontology']['CSO_PATH'])
    
    def get_cso_pickle_path(self):
        return os.path.join(self.dir, self.config['Ontology']['CSO_PICKLE_PATH'])
    
    def get_cso_remote_url(self):
        return self.config['Ontology']['CSO_REMOTE_URL']
    
    def get_ontology_version(self):
        return self.config['Ontology']['CSO_VERSION']
    
    def set_cso_version(self, version):
        self.config['Ontology']['CSO_VERSION'] = version
        self.write_config_file()

# =============================================================================
#     MODEL  
# =============================================================================
    def get_model_pickle_path(self):
        return os.path.join(self.dir, self.config['Model']['MODEL_PICKLE_PATH'])
    
    def get_model_pickle_remote_url(self):
        return self.config['Model']['MODEL_PICKLE_REMOTE_URL']
    
    def get_cached_model(self):
        return os.path.join(self.dir, self.config['Model']['CACHED_MODEL'])
    
    def get_cahed_model_remote_url(self):
        return self.config['Model']['CACHED_MODEL_REMOTE_URL']
    
# =============================================================================
#     READ AND WRITE CONFIG FILE
# =============================================================================
    def read_config_file(self):
        self.config.read(self.config_file)
        
    def write_config_file(self):
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)