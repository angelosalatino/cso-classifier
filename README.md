# CSO-Classifier

Classifying research papers according to their research topics is an important task to improve their retrievability, assist the creation of smart analytics, and support a variety of approaches for analysing and making sense of the research environment. In this repository, we present the CSO Classifier, a new unsupervised approach for automatically classifying research papers according to the [Computer Science Ontology (CSO)](https://cso.kmi.open.ac.uk), a comprehensive ontology of research areas in the field of Computer Science. The CSO Classifier takes as input the metadata associated with a research paper (title, abstract, keywords) and returns a selection of research concepts drawn from the ontology. The approach was evaluated on a gold standard of manually annotated articles yielding a significant improvement over alternative methods.


## About

The CSO Classifier is a novel application that takes as input the text from abstract, title, and keywords of a research paper and outputs a list of relevant concepts from CSO. It consists of two main components: (i) the syntactic module and (ii) the semantic module. Figure 1 depicts its architecture. The syntactic module parses the input documents and identifies CSO concepts that are explicitly referred in the document. The semantic module uses part-of-speech tagging to identify promising terms and then exploits word embeddings to infer semantically related topics. Finally, the CSO Classifier combines the results of these two modules and enhances them by including relevant super-areas.

![Framework of CSO Classifier](/images/Workflow.png "Framework of CSO Classifier")

## Requirements
1. Ensure you have [**Python 3**](https://www.python.org/downloads/) installed.
2. Install the necessary depepencies by executing the following command:```pip install -r requirements.txt```
3. Download English package for spaCy using ```python -m spacy download en_core_web_sm```


## Main Files
* **CSO-Classifier.ipynb**: :page_facing_up: Python notebook for executing the classifier
* **requirements.txt**: :page_facing_up: File containing the necessary libraries to run the classifier
*  **images**: :file_folder: folder containing some pictures, e.g., the workflow showed above
*  **classifier**: :file_folder: Folder containing the main functionalities of the classifier
    - **syntacticmodule.py**: :page_facing_up: functionalities that implement the syntactic module
    - **semanticmodule.py**: :page_facing_up: functionalities that implement the semantic module
    - **misc.py**: :page_facing_up: some miscellaneous functionalities
    - **models**: :file_folder: Folder containing the word2vec model and CSO
        - **cso.csv**: :page_facing_up: file containing the Computer Science Ontology in csv
        - **cso.p**: :page_facing_up: serialised file containing the Computer Science Ontology (pickled)
        - **token-to-cso-combined.json**: :page_facing_up: file containing the cached word2vec model. This json file contains a dictionary in which each token of the corpus vocabulary, has been mapped with the corresponding CSO topics. Below we explain how this file has been generated.

## Generation of the model and token-to-cso-combined file
In this section we describe how we generated the word2vec model used within the CSO Classifier and what is the token-to-cso-combined file.

### Word Embedding generation
We applied the word2vec approach [1,2] to a collection of text from the Microsoft Academic Graph (MAG)  for generating word embeddings. MAG is a scientific knowledge base and a heterogeneous graph containing scientific publication records, citation relationships, authors, institutions, journals, conferences, and fields of study. It is the largest dataset of scholarly data publicly available, and, as of December 2018, it contains more than 210 million publications.
We first downloaded titles, and abstracts of 4,654,062 English papers in the field of Computer Science. Then we pre-processed the data by replacing spaces with underscores in all n-grams matching the CSO topic labels (e.g., “digital libraries” became “digital_libraries”) and for frequent bigrams and trigrams (e.g., “highest_accuracies”, “highly_cited_journals”). These frequent n-grams were identified by analysing combinations of words that co-occur together, as suggested in [2] and using the parameters showed in Table 1. Indeed, while it is possible to obtain the vector of a n-gram by averaging the embedding vectors of all it words, the resulting representation usually is not as good as the one obtained by considering the n-gram as a single word during the training phase. 
Finally, we trained the word2vec model using the parameters provided in Table 2. The parameters were set to these values after testing several combinations. 


| min-count  |  threshold |
|---|---|
| 5  | 10  |

Table 1: Parameters used during the collocation words analysis


| method  |  emb. size | window size | min count cutoff |
|---|---|---|---|
| skipgram  | 128  |  10 |  10 |

Table 2: Parameters used for training the word2vec model.


After training the model we obtained a **gensim.models.keyedvectors.Word2VecKeyedVectors** object weighing **366MB**. You can download the model [from here](https://cso.kmi.open.ac.uk/download/model.p). 
The size of the model hindered the performance of the classifier in two ways. Firstly, it required several seconds to be loaded into memory. This was partially fixed by serialising the model file (using python pickle, see version v2.0 of CSO Classifier). Secondly, while processing a document, the classifier needs to retrieve the top 10 similar words for all tokens, and compare them with CSO topics. In performing such operation, the model would recquire several seconds, becoming a bottleneck for the classification process.
To this end, we decided to create a cached model (**token-to-cso-combined.json**) which is a dictionary that directly connects all token available in the vocabulary of the model with the CSO topics. This strategy allows to quickly retrieve all CSO topics that can be inferred by a particular token.

### token-to-cso-combined file

To generate this file, we collected all the set of words available within the vocabulary of the model. Then iterating on each word, we retrieved its top 10 similar words from the model, and we computed their Levenshtein similarity against all CSO topics. If the similarity was above 0.7, we created a record which stored all CSO topics triggered by the initial word.


## Input - Output
### Sample Input
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

### Sample Output
```json
{
    "syntactic": [
        "sensitive informations",
        "graph theory",
        "real-world networks",
        "network topology",
        "social networks",
        "anonymity",
        "anonymization",
        "twitter",
        "microblogging",
        "privacy",
        "data privacy",
        "online social networks",
        "data mining"
    ],
    "semantic": [
        "social networks",
        "online social networks",
        "data mining",
        "privacy",
        "data privacy",
        "anonymization",
        "anonymity",
        "twitter",
        "microblogging",
        "topology",
        "network topology",
        "graph theory",
        "network architecture",
        "network structures",
        "social networking sites",
        "association rules",
        "micro-blog"
    ],
    "union": [
        "sensitive informations",
        "social networking sites",
        "micro-blog",
        "network architecture",
        "graph theory",
        "social networks",
        "network topology",
        "real-world networks",
        "topology",
        "anonymity",
        "anonymization",
        "association rules",
        "twitter",
        "microblogging",
        "network structures",
        "privacy",
        "data privacy",
        "online social networks",
        "data mining"
    ],
    "enhanced": [
        "complex networks",
        "privacy preserving",
        "world wide web",
        "theoretical computer science",
        "social media",
        "network protocols",
        "access control",
        "security of data",
        "online systems",
        "electric network topology",
        "computer science",
        "facebook",
        "network security",
        "neural networks",
        "authentication"
    ]
}
```

## References

[1] Mikolov, T., Chen, K., Corrado, G. and Dean, J. 2013. Efficient Estimation of Word Representations in Vector Space. (Jan. 2013).
[2]	Mikolov, T., Chen, K., Corrado, G. and Dean, J. 2013. Distributed Representations of Words and Phrases and their Compositionality. Advances in neural information processing systems. 3111–3119.
