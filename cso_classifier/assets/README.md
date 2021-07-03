# Model Folder

This folder contains the ontology and word2vec model. Initially, this folder will be **empty**, and it will be filled with files downloaded from remote once the setup is complete.

In particular, after installing the classifier, this folder will contain:
* **cso.csv**
* **cso.p**
* **cso_graph.p**
* **token-to-cso-combined.json**
* **model.p**


## cso.csv
This file contains the Computer Science Ontology describing the relationships between different research concepts. Each row contains a triple (subject, predicate, object).

## cso.p
This serialized file contains the Computer Science Ontology. In particular, it contains a dictionary with all the relevant information about the different concepts included in CSO. It is produced from the file *cso.csv*. This file has been created using [Pickle](https://docs.python.org/3/library/pickle.html). Serializing such object allows us to quickly import it in our workspace.

## cso_graph.p
This serialized file contains the Computer Science Ontology structured as a graph (iGraph object). This object will be used during the post-processing phase.

## token-to-cso-combined.json
This file contains a dictionary that matches all tokens with the CSO topics. This is a cached file generated from the original trained word2vec model. Contrary to the previous version of the classifier, this cache allows to save time as the classifier knows what topics can be triggered by a particular word.

## model.p
This serialized file contains the word2vec model. It will be loaded and used only within the outlier detection component in the post-processing module.
 

## In case of ERROR
If by any chance, this folder is still empty after the setup, please run:

```python
from cso_classifier import CSOClassifier as cc
cc.update(force = True)
```

This will force the download of all files.