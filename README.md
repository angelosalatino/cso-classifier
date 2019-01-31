# CSO-Classifier

Classifying research papers according to their research topics is an important task to improve their retrievability, assist the creation of smart analytics, and support a variety of approaches for analysing and making sense of the research environment. In this repository, we present the CSO Classifier, a new unsupervised approach for automatically classifying research papers according to the [Computer Science Ontology (CSO)](https://cso.kmi.open.ac.uk), a comprehensive ontology of research areas in the field of Computer Science. The CSO Classifier takes as input the metadata associated with a research paper (title, abstract, keywords) and returns a selection of research concepts drawn from the ontology. The approach was evaluated on a gold standard of manually annotated articles yielding a significant improvement over alternative methods.


## About

The CSO Classifier is a novel application that takes as input the text from abstract, title, and keywords of a research paper and outputs a list of relevant concepts from CSO. It consists of two main components: (i) the syntactic module and (ii) the semantic module. Figure 1 depicts its architecture. The syntactic module parses the input documents and identifies CSO concepts that are explicitly referred in the document. The semantic module uses part-of-speech tagging to identify promising terms and then exploits word embeddings to infer semantically related topics. Finally, the CSO Classifier combines the results of these two modules and enhances them by including relevant super-areas.

![Framework of CSO Classifier](/v2/images/Workflow.png "Framework of CSO Classifier")


## Repository Structure
* In **v1 folder** you can find the find version of the classifier published as [poster paper at ISWC 2018](http://oro.open.ac.uk/55908/). This classifier finds all topics in the ontology that are explicitly mentioned within the processed papers.
* In **v2 folder** you can find the second version submitted to JCDL 2019. [Pre-print](http://skm.kmi.open.ac.uk/the-cso-classifier-ontology-driven-detection-of-research-topics-in-scholarly-articles/). This classifier instead analyzes papers both on a syntactic and semantic level, and returns a set of pertinent research topics drawn from CSO.

## Main Requirements
1. Ensure you have [**Python 3**](https://www.python.org/downloads/) installed.
2. Each folder will have its own *requirements.txt* file, including all necessary dependencies. Install them by executing the following command:```pip install -r requirements.txt```.

## Other Links and Relevant Papers
* [Computer Science Ontology (CSO)](https://cso.kmi.open.ac.uk)
* [Classifying Research Papers with the Computer Science Ontology](http://oro.open.ac.uk/55908/). In (ISWC 2018 Posters & Demonstrations and Industry Tracks) @ The 17th International Semantic Web Conference (ISWC 2018), 8-12 October 2018, Monterey, California, USA, 2018
* [The CSO Classifier: Ontology-Driven Detection of Research Topics in Scholarly Articles](http://skm.kmi.open.ac.uk/the-cso-classifier-ontology-driven-detection-of-research-topics-in-scholarly-articles/). *Submitted to JCDL 2019*

## How to cite this work
If you use the CSO Classfier in your research or work and would like to cite the SKM3 Application Programming Interface, we suggest you cite:
* Salatino, Angelo; Thanapalasingam, Thiviyan; Mannocci, Andrea; Osborne, Francesco and Motta, Enrico (2018). **Classifying Research Papers with the Computer Science Ontology.** In: *ISWC 2018 Posters & Demonstrations and Industry Tracks* (van Erp, Marieke ed.).