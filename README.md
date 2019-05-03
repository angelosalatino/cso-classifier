# CSO-Classifier

Classifying research papers according to their research topics is an important task to improve their retrievability, assist the creation of smart analytics, and support a variety of approaches for analysing and making sense of the research environment. In this repository, we present the CSO Classifier, a new unsupervised approach for automatically classifying research papers according to the [Computer Science Ontology (CSO)](https://cso.kmi.open.ac.uk), a comprehensive ontology of research areas in the field of Computer Science. The CSO Classifier takes as input the metadata associated with a research paper (title, abstract, keywords) and returns a selection of research concepts drawn from the ontology. The approach was evaluated on a gold standard of manually annotated articles yielding a significant improvement over alternative methods.


## About

The CSO Classifier is a novel application that takes as input the text from abstract, title, and keywords of a research paper and outputs a list of relevant concepts from CSO. It consists of two main components: (i) the syntactic module and (ii) the semantic module. Figure 1 depicts its architecture. The syntactic module parses the input documents and identifies CSO concepts that are explicitly referred in the document. The semantic module uses part-of-speech tagging to identify promising terms and then exploits word embeddings to infer semantically related topics. Finally, the CSO Classifier combines the results of these two modules and enhances them by including relevant super-areas.

![Framework of CSO Classifier](/images/Workflow.png "Framework of CSO Classifier")

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
        - **model.p**: :page_facing_up: file containing the word2vec model. Please be aware that this file is not currently tracked within this repository due to its large size (over 100MB). This file needs to be downloaded separately (see ```Requirements #4``` above). 


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