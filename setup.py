import setuptools
import configparser

with open("README.md", "r") as fh:
    long_description = fh.read()


requirements_to_install = [
    'click==7.1.2',
    'gensim==3.8.1',
    'hurry.filesize==0.9',
    'kneed==0.3.1',
    'nltk==3.6.2',
    'python-igraph==0.9.1',
    'python-Levenshtein==0.12.2',
    'numpy>=1.19.5',
    'requests==2.25.1',
    'spacy==3.0.5',
    'strsimpy==0.2.0',
    'update-checker==0.18.0'
]


# Import version number from version.py
config = configparser.ConfigParser()
config.read("cso_classifier/config.ini")
__version__ = config['classifier']['classifier_version']


setuptools.setup(
    name="cso-classifier",
    version=__version__,
    author="Angelo Salatino",
    author_email="angelo.salatino@open.ac.uk",
    description="A light-weight Python app for classifying scientific documents with the topics from the Computer Science Ontology (https://cso.kmi.open.ac.uk/home).",
    long_description=long_description,
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
    python_requires='>=3.6.0',
)