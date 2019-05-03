# Model Folder

This folder should contain three files:
* **cso.csv**
* **cso.p**
* **model.p**

The last two files contain a serialized Python object, created using [Pickle](https://docs.python.org/3/library/pickle.html). Serializing such objects allows us to quickly import them in our workspace.

## cso.csv
This file contains the Computer Science Ontology describing the relationships between different research concepts. Each row contains a triple (subject, predicate, object).

## cso.p
This serialized file contains the Computer Science Ontology. In particular, it contains a dictionary with all the relevant information about the different concepts included in CSO. It is produced from the file *cso.csv*.

## model.p
This serialized file contains the word2vec model that has been trained using the Gensim library:

```
gensim.models.keyedvectors.Word2VecKeyedVectors
```

### Why the model.p file is not the repository?

This is the reason why we stated "should contain", at the beginning. 
Unfortunately, due to its size (~350MB), it cannot be loaded on Github. To this end, we are storing it on one of [our servers](https://cso.kmi.open.ac.uk/download/model.p). To use the CSO Classifier v2, it is important that you download this model first.
However, for users' convenience this file will be automatically downloaded at the first run of the classifier. Indeed, the function ```load_ontology_and_model()``` will check if the model is present, if not it will proceed to download it.
