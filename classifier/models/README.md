# Model Folder

This folder contains three files:
* **cso.csv**
* **cso.p**
* **token-to-cso-combined.json**


## cso.csv
This file contains the Computer Science Ontology describing the relationships between different research concepts. Each row contains a triple (subject, predicate, object).

## cso.p
This serialized file contains the Computer Science Ontology. In particular, it contains a dictionary with all the relevant information about the different concepts included in CSO. It is produced from the file *cso.csv*. This file has been created using [Pickle](https://docs.python.org/3/library/pickle.html). Serializing such object allows us to quickly import it in our workspace.

## token-to-cso-combined.json
This file contains a dictionary that matches all tokens with the CSO topics. Contrary to the previous version of the classifier, this cache allows to save time as the classifier knows what topics can be triggered by a particular word.

### Why the word2vec (model) file is not the repository?
After training the word2vec model, it resulted quite cumbersome (~366MB). It was taking time to load into memory and during processing time it required some time to check similarity between words and thus retrieving the top 10 similar workds. To This end we shifted to a cached version which would allow us to save time at processing time.
However, we published the model file and it could be downloaded from [our servers](https://cso.kmi.open.ac.uk/download/model.p). 
