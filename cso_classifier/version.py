"""
This module exposes the version of the CSO Classifier package.
"""
from cso_classifier.config import Config

__version__: str = Config().get_classifier_version()