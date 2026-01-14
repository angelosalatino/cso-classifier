"""
Setup Script for CSO Classifier
===============================

This script handles the packaging, distribution, and installation of the 
CSO Classifier, a Python application for classifying scientific documents 
using the Computer Science Ontology (CSO).

Key Functionalities:
--------------------
1.  **Metadata Retrieval**: Reads the project's `README.md` to provide a 
    detailed long description for PyPI and other package managers.
2.  **Dependency Management**: Specifies a list of required Python packages 
    (e.g., `gensim`, `spacy`, `nltk`) ensuring all necessary libraries are 
    installed automatically.
3.  **Version Control**: Extracts the current version number dynamically from 
    `cso_classifier/config.ini` to maintain consistency between the code 
    and the package metadata.
4.  **Package Configuration**: Uses `setuptools.setup()` to define package 
    attributes such as name, author, license, and included data files 
    (assets and config).

Usage:
------
To install the package locally in editable mode:
    $ pip install -e .

To build a source distribution:
    $ python setup.py sdist

To build a wheel:
    $ python setup.py bdist_wheel
"""
import io
import os
import setuptools
import configparser

# --- Long description (robust UTF-8, fallback if README missing) ---
readme = ""
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
if os.path.exists(readme_path):
    with io.open(readme_path, "r", encoding="utf-8") as fh:
        readme = fh.read()
else:
    readme = "CSO Classifier: classify scientific documents with topics from the Computer Science Ontology."



requirements_to_install = [
    # Note: Versions are pinned to ensure stability and reproducibility.
    'igraph==0.10.4',
    'gensim==4.3.3',
    'click==7.1.2',
    'hurry.filesize==0.9',
    'kneed==0.3.1',
    'nltk==3.6.2',
    'rapidfuzz==2.11.1',
    'numpy>=1.19.5',
    'requests==2.25.1',
    'spacy==3.8.7',
    'strsimpy==0.2.0',
    'update-checker==0.18.0'
]


# --- Read version from config.ini (UTF-8 encoded) ---
config = configparser.ConfigParser()
config.read(os.path.join("cso_classifier", "config.ini"), encoding="utf-8")
__version__ = config["classifier"]["classifier_version"]


setuptools.setup(
    name="cso-classifier",
    version=__version__,
    author="Angelo Salatino",
    author_email="angelo.salatino@open.ac.uk",
    description="A light-weight Python app for classifying scientific documents with the topics from the Computer Science Ontology (https://cso.kmi.open.ac.uk/home).",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/angelosalatino/cso-classifier",
    packages=['cso_classifier'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    package_data = {'cso_classifier' : ['assets/*','config.ini'] },
    install_requires=requirements_to_install,
    license="Apache-2.0",
    python_requires='>=3.11.0',
)