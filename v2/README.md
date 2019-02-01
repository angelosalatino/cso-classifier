# CSO-Classifier

Classifying scholarly papers according to the relevant research topics is an important task that enables a multitude of functionalities, such as: (i) categorising proceedings in digital libraries, (ii) enhancing semantically the metadata of scientific publications, (iii) generating recommendations, (iv) producing smart analytics, (v) detecting research trends, and others. 
In this folder, we present the CSO Classifier, a new approach for automatically classifying research papers according to the [Computer Science Ontology (CSO)](https://cso.kmi.open.ac.uk).

## About
The CSO Classifier takes as input the metadata associated with a scholarly article (usually title, abstract, and keywords) and returns a selection of research topics drawn from CSO. It operates in three steps. First, it finds all topics in the ontology that are explicitly mentioned in the paper. Then it identifies further semantically related topics by utilizing part-of-speech tagging and world embeddings. Finally, it enriches this set by including the super-areas of these topics according to CSO.

![Workflow of CSO Classifier](/v2/images/Workflow.png "Workflow of CSO Classifier")

## Requirements
1. Ensure you have [**Python 3**](https://www.python.org/downloads/) installed.
2. Install the necessary depepencies by executing the following command:```pip install -r requirements.txt```
3. Download English package for spaCy using ```python -m spacy download en_core_web_sm```
4. Download the word2vec model. The current model has a size of 350MB and cannot be stored in Github. For this reason it must be downloaded separately from [https://cso.kmi.open.ac.uk/download/model.p](https://cso.kmi.open.ac.uk/download/model.p) and stored in the *models* folder: ```/classifier/models/```

## Main Files
* **CSO-Classifier.ipynb**: :page_facing_up: Python notebook for executing the classifier
* **requirements.txt**: :page_facing_up: File containing the necessary libraries to run the classifier
*  **images**: :file_folder: folder containing some pictures, e.g., the workflow showed above
*  **classifier**: :file_folder: Folder containing the main functionalities of the classifier
    - **syntacticmodule.py**: :page_facing_up: functionalities that implement the syntactic module
    - **semanticmodule.py**: :page_facing_up: functionalities that implement the semantic module
    - **misc.py**: :page_facing_up: some miscellaneous functionalities
    - **models**: :file_folder: Folder containing the word2vec model and CSO
        - **cso.p**: :page_facing_up: file containing the Computer Science Ontology
        - **model.P**: :page_facing_up: file containing the word2vec model. Please be aware that this file is not currently tracked within this repository due to its large size (over 100MB). This file needs to be downloaded separately (see ```Requirements #4``` above). 


## Sample Input
```json
paper = {
        "title": "De-anonymizing Social Networks",
        "abstract": "Operators of online social networks are increasingly sharing potentially "
        "sensitive information about users and their relationships with advertisers, application "
        "developers, and data-mining researchers. Privacy is typically protected by anonymization, "
        "i.e., removing names, addresses, etc. We present a framework for analyzing privacy and "
        "anonymity in social networks and develop a new re-identification algorithm targeting "
        "anonymized social-network graphs. To demonstrate its effectiveness on real-world networks, "
        "we show that a third of the users who can be verified to have accounts on both Twitter, a "
        "popular microblogging service, and Flickr, an online photo-sharing site, can be re-identified "
        "in the anonymous Twitter graph with only a 12% error rate. Our de-anonymization algorithm is "
        "based purely on the network topology, does not require creation of a large number of dummy "
        "\"sybil\" nodes, is robust to noise and all existing defenses, and works even when the overlap "
        "between the target network and the adversary's auxiliary information is small.",
        "keywords": "data mining, data privacy, graph theory, social networking (online)"
        }
```

## Sample Output
```json
{
    "syntactic": [
        "twitter",
        "graph theory",
        "data mining",
        "anonymization",
        "online social networks",
        "data privacy",
        "network topology",
        "anonymity",
        "sensitive informations",
        "microblogging",
        "social networks",
        "privacy",
        "real-world networks"
    ],
    "semantic": [
        "social networks",
        "online social networks",
        "sensitive informations",
        "data mining",
        "privacy",
        "data privacy",
        "anonymization",
        "anonymity",
        "network topology",
        "twitter",
        "microblogging",
        "topology",
        "graph theory",
        "social media",
        "social networking sites",
        "network structures",
        "network architecture",
        "micro-blog",
        "online communities",
        "social graphs"
    ],
    "union": [
        "network architecture",
        "data privacy",
        "network topology",
        "graph theory",
        "micro-blog",
        "network structures",
        "social graphs",
        "microblogging",
        "topology",
        "twitter",
        "social networks",
        "social media",
        "data mining",
        "online social networks",
        "privacy",
        "social networking sites",
        "anonymization",
        "anonymity",
        "sensitive informations",
        "real-world networks",
        "online communities"
    ],
    "enhanced": [
        "privacy preserving",
        "complex networks",
        "online systems",
        "facebook",
        "computer science",
        "access control",
        "neural networks",
        "electric network topology",
        "world wide web",
        "network security",
        "security of data",
        "authentication",
        "network protocols",
        "theoretical computer science"
    ]
}
```