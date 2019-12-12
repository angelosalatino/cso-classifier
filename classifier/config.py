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
        return self.config['Classifier']['classifier_version']
    
    def get_package_name(self):
        return self.config['Classifier']['package_name']
    
    def set_classifier_version(self, version):
        self.config['Classifier']['classifier_version'] = version
        self.write_config_file()

# =============================================================================
#     ONTOLOGY
# =============================================================================
    def get_cso_path(self):
        return os.path.join(self.dir, self.config['Ontology']['cso_path'])
    
    def get_cso_pickle_path(self):
        return os.path.join(self.dir, self.config['Ontology']['cso_pickle_path'])
    
    def get_cso_remote_url(self):
        return self.config['Ontology']['cso_remote_url']
    
    def get_ontology_version(self):
        return self.config['Ontology']['cso_version']
    
    def get_cso_version_logger_url(self):
        return self.config['Ontology']['cso_versions_logger_url']
    
    def set_cso_version(self, version):
        self.config['Ontology']['cso_version'] = version
        self.write_config_file()

# =============================================================================
#     MODEL  
# =============================================================================
    def get_model_pickle_path(self):
        return os.path.join(self.dir, self.config['Model']['model_pickle_path'])
    
    def get_model_pickle_remote_url(self):
        return self.config['Model']['model_pickle_remote_url']
    
    def get_cached_model(self):
        return os.path.join(self.dir, self.config['Model']['cached_model'])
    
    def get_cahed_model_remote_url(self):
        return self.config['Model']['cached_model_remote_url']
    
# =============================================================================
#     READ AND WRITE CONFIG FILE
# =============================================================================
    def read_config_file(self):
        self.config.read(self.config_file)
        
    def write_config_file(self):
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)