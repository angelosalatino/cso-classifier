"""
CSO Classifier Package
======================

The `cso_classifier` package provides a tool for automatically classifying research papers 
according to the Computer Science Ontology (CSO). It leverages both syntactic and semantic 
modules to identify relevant research topics from metadata such as titles, abstracts, and keywords.

Main Components:
----------------
- **CSOClassifier**: The main class for running the classification process on single or multiple papers.
- **Ontology**: Manages the Computer Science Ontology (CSO) data.
- **Model**: Manages the Word2Vec model used for semantic analysis.

Utilities:
----------
- **test_classifier_single_paper**: Helper function to test the classifier on a single sample paper.
- **test_classifier_batch_mode**: Helper function to test the classifier on a batch of sample papers.

Exposed Classes and Functions:
------------------------------
The package exposes the following classes and functions for direct import:
- `CSOClassifier`
- `Ontology`
- `Model`
- `Paper`
- `Result`
- `Config`
- `Semantic`
- `Syntactic`
- `PostProcess`
- `test_classifier_single_paper`
- `test_classifier_batch_mode`

Version:
--------
- `__version__`: The current version of the CSO Classifier.
"""
from .classifier import CSOClassifier
from .misc import chunks, download_language_model, print_header
from .semanticmodule import Semantic
from .syntacticmodule import Syntactic
from .postprocmodule import PostProcess
from .ontology import Ontology
from .model import Model
from .paper import Paper
from .result import Result
from .config import Config
from .test import test_classifier_single_paper, test_classifier_batch_mode


from .version import __version__