import configparser
import os



class Config:
    """ A simple abstraction layer for the configuration file """

    def __init__(self) -> None:
        """ Initialising the Config class.
        """
        self.dir = os.path.dirname(os.path.realpath(__file__))
        self.config_file = os.path.join(self.dir, "config.ini")
        self.config = configparser.ConfigParser()
        self.read_config_file()

# =============================================================================
#     CLASSIFIER
# =============================================================================
    def get_classifier_version(self) -> str:
        """ Returns the version of the classifier.

        Returns:
            str: The version of the classifier.
        """
        return self.config['classifier']['classifier_version']

    def get_package_name(self) -> str:
        """ Returns the package name.

        Returns:
            str: The package name.
        """
        return self.config['classifier']['package_name']

    def set_classifier_version(self, version: str) -> None:
        """ Sets the version of the classifier.

        Args:
            version (str): The new version string.
        """
        self.config['classifier']['classifier_version'] = version
        self.write_config_file()

# =============================================================================
#     ONTOLOGY
# =============================================================================
    def get_cso_path(self) -> str:
        """ Returns the path of the local version of CSO.

        Returns:
            str: The file path to the local CSO CSV file.
        """
        return os.path.join(self.dir, self.config['ontology']['cso_path'])

    def get_cso_pickle_path(self) -> str:
        """ Returns the path of the local pickle version of CSO.

        Returns:
            str: The file path to the local CSO pickle file.
        """
        return os.path.join(self.dir, self.config['ontology']['cso_pickle_path'])

    def get_cso_graph_path(self) -> str:
        """ Returns the path of the local pickle version of CSO (GRAPH).

        Returns:
            str: The file path to the local CSO graph pickle file.
        """
        return os.path.join(self.dir, self.config['ontology']['cso_graph_path'])

    def get_cso_remote_url(self) -> str:
        """ Returns the remote url where the latest version of CSO is located.

        Returns:
            str: The remote URL for CSO.
        """
        return self.config['ontology']['cso_remote_url']

    def get_ontology_version(self) -> str:
        """ Return the ontology version.

        Returns:
            str: The ontology version.
        """
        return self.config['ontology']['cso_version']

    def get_cso_version_logger_url(self) -> str:
        """ Returns the url of the version logger of CSO.

        Returns:
            str: The URL for the CSO version logger.
        """
        return self.config['ontology']['cso_versions_logger_url']

    def set_cso_version(self, version: str) -> None:
        """ Sets the CSO version.

        Args:
            version (str): The new version string.
        """
        self.config['ontology']['cso_version'] = version
        self.write_config_file()

# =============================================================================
#     MODEL
# =============================================================================
    def get_model_pickle_path(self) -> str:
        """ Returns the local path of the pickle model.

        Returns:
            str: The file path to the local model pickle file.
        """
        return os.path.join(self.dir, self.config['model']['model_pickle_path'])

    def get_model_pickle_remote_url(self) -> str:
        """ Returns the remote url of the pickle model.

        Returns:
            str: The remote URL for the model pickle file.
        """
        return self.config['model']['model_pickle_remote_url']

    def get_cached_model(self) -> str:
        """ Returns the local path of the cached model.

        Returns:
            str: The file path to the local cached model file.
        """
        return os.path.join(self.dir, self.config['model']['cached_model'])

    def get_cahed_model_remote_url(self) -> str:
        """ Returns the remote url of the cached model.

        Returns:
            str: The remote URL for the cached model file.
        """
        return self.config['model']['cached_model_remote_url']

# =============================================================================
#     READ AND WRITE CONFIG FILE
# =============================================================================
    def read_config_file(self) -> None:
        """ Reads the config file.
        """
        self.config.read(self.config_file)

    def write_config_file(self) -> None:
        """ Writes the config file.
        """
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)
