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
4. Download the word2vec model. The current model has a size of 350MB and cannot be stored in Github. For this reason it must be downloaded separately from [https://cso.kmi.open.ac.uk/downloads/model.p](https://cso.kmi.open.ac.uk/downloads/model.p) and stored in the *models* folder: ```/classifier/models/```

## Main Files
* **CSO-Classifier.ipynb**: :page_facing_up: Python notebook for executing the classifier
* **requirements.txt**: :page_facing_up: File containing the necessary libraries to run the classifier
*  **classifier**: :file_folder: Folder containing the main functionalities of the classifier
    - **syntacticmodule.py**: :page_facing_up: functionalities that implement the syntactic module
    - **semanticmodule.py**: :page_facing_up: functionalities that implement the semantic module
    - **misc.py**: :page_facing_up: some miscellaneous functionalities
    - **models**: :file_folder: Folder containing the word2vec model and CSO
        - **cso.p**: :page_facing_up: file containing the Computer Science Ontology
        - **model.P**: :page_facing_up: file containing the word2vec model. Please be aware that this file is not currently tracked within this repository due to its large size (over 100MB). This file needs to be downloaded separately (see ```Requirements #4``` above). 