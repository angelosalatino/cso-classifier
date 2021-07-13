# CSO-Classifier

[![PyPI version](https://badge.fury.io/py/cso-classifier.svg)](https://badge.fury.io/py/cso-classifier) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.2660819.svg)](https://doi.org/10.5281/zenodo.2660819)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Abstract

Classifying research papers according to their research topics is an important task to improve their retrievability, assist the creation of smart analytics, and support a variety of approaches for analysing and making sense of the research environment. In this repository, we present the CSO Classifier, a new unsupervised approach for automatically classifying research papers according to the [Computer Science Ontology (CSO)](https://cso.kmi.open.ac.uk), a comprehensive ontology of research areas in the field of Computer Science. The CSO Classifier takes as input the metadata associated with a research paper (title, abstract, keywords) and returns a selection of research concepts drawn from the ontology. The approach was evaluated on a gold standard of manually annotated articles yielding a significant improvement over alternative methods.

## Table of contents

<!--ts-->
* [Abstract](#abstract)
* [Table of contents](#table-of-contents)
* [About](#about)
* [Getting started](#getting-started)
  * [Installation using PIP](#installation-using-pip)
  * [Installation using Github](#installation-using-github)
  * [Troubleshooting](#troubleshooting)
  * [Setup](#setup)
  * [Update](#update)
  * [Version](#version)
  * [Test](#test)
* [Usage examples](#usage-examples)
  * [Classifying a single paper (SP)](#classifying-a-single-paper-sp)
  * [Classifying in batch mode (BM)](#classifying-in-batch-mode-bm)
  * [Parameters](#parameters)
* [Releases](#releases)
  * [v3.0](#v30)
  * [v2.3.2](#v232)
  * [v2.3.1](#v231)
  * [v2.3](#v23)
  * [v2.2](#v22)
  * [v2.1](#v21)
  * [v2.0](#v20)
  * [v1.0](#v10)
* [List of Files](#list-of-files)
* [Word2vec model and token-to-cso-combined file generation](#word2vec-model-and-token-to-cso-combined-file-generation)
  * [Word Embedding generation](#word-embedding-generation)
  * [token-to-cso-combined file](#token-to-cso-combined-file)
* [Use the CSO Classifier in other domains of Science](#use-the-cso-classifier-in-other-domains-of-science)
* [How to Cite CSO Classifier](#how-to-cite-cso-classifier)
* [License](#license)
* [References](#references)
<!--te-->

## About

The CSO Classifier is a novel application that takes as input the text from the abstract, title, and keywords of a research paper and outputs a list of relevant concepts from CSO. It consists of three main components: (i) the syntactic module, (ii) the semantic module and (iii) the post-processing module. Figure 1 depicts its architecture. The syntactic module parses the input documents and identifies CSO concepts that are explicitly referred to in the document. The semantic module uses part-of-speech tagging to identify promising terms and then exploits word embeddings to infer semantically related topics. Finally, the post-processing module combines the results of these two modules, removes outliers, and enhances them by including relevant super-areas.

![Framework of CSO Classifier](https://github.com/angelosalatino/cso-classifier/raw/master/images/Workflow.png "Framework of CSO Classifier")
**Figure 1**: Framework of CSO Classifier

## Getting started

### Installation using PIP

1. Ensure you have **Python 3.6** or above installed. Download [latest version](https://www.python.org/downloads/). Perhaps, you may want to use a virtual environment. Here is how to [create and activate](https://docs.python.org/3/tutorial/venv.html) a virtual environment.
2. Use pip to install the classifier: ```pip install cso-classifier```
3. Setting up the classifier. Go to [Setup](#setup) for finalising the installation.

### Installation using Github

1. Ensure you have [**Python 3.6**](https://www.python.org/downloads/) or above installed. Download [latest version](https://www.python.org/downloads/). Perhaps, you may want to use a virtual environment. Here is how to [create and activate](https://docs.python.org/3/tutorial/venv.html) a virtual environment.
2. Download this repository using: ```git clone https://github.com/angelosalatino/cso-classifier.git```
3. Install the package by running the following command: ```pip install ./cso-classifier```
4. Setting up the classifier. Go to [Setup](#setup) for finalising the installation.

### Troubleshooting

Although, we have worked hard to fix many issues occurring at testing phase, some of them could still arise for reasons that go beyond our control. Here is the list of the common issues we have encountered.

#### Unable to install requirements

Most likely this issue is due to the version of ```pip``` you are currently using. Make sure to update to the latest version of pip: ```pip install --upgrade pip```.

#### Unable to install python-Levenshtein

Many users found difficulties in installing the python-Levenshtein library on some Linux servers. One way to get around this issue is to install the ```python3-devel``` package. You might need sudo rights on the hosting machine.

-- Special thanks to Panagiotis Mavridis for suggesting the solution.

#### "python setup.py egg_info" failed

More specifically: ```Command "python setup.py egg_info" failed with error code 1```. This error is due to the *setup.py* file. The occurrence of this issue is rare. If you are experiencing it, please do get in touch with us. We will work with you to fix it.

### Setup

After installing the CSO Classifier, it is important to set it up with the right dependencies. To set up the classifier, please run the following code:

```python
from cso_classifier import CSOClassifier as cc
cc.setup()
exit() # it is important to close the current console, to make those changes effective
```

This function downloads the English package of spaCy, which is equivalent to run ```python -m spacy download en_core_web_sm```.
Then, it downloads the latest version of Computer Science Ontology and the latest version of the word2vec model, which will be used across all modules.

### Update

This functionality allows to update both ontology and word2vec model.

```python
from cso_classifier import CSOClassifier as cc
cc.update()

#or
cc.update(force = True)
```

By just running ```update()``` without parameters, the system will check the version of the ontology/model that is currently using, against the lastest available version. The update will be performed if one of the two or both are outdated.
Instead with ```update(force = True)``` the system will force the update by deleting the ontology/model that is currently using, and downloading their latest version.

### Version

This functionality returns the version of the CSO Classifier and CSO ontology you are currently using. It will also check online if there is a newer version, for both of them, and suggest how to update.

```python
from cso_classifier import CSOClassifier as cc
cc.version()
```

Instead, if you just want to know the package version use:
```python
import cso_classifier
print(cso_classifier.__version__)
```

### Test

This functionality allows you to test whether the classifier has been properly installed.

```python
import cso_classifier as test
test.test_classifier_single_paper() # to test it with one paper
test.test_classifier_batch_mode() # to test it with multiple papers
```

To ensure that the classifier has been installed successfully, these two functions ```test_classifier_single_paper()``` and ```test_classifier_batch_mode()``` print out both paper(s) info and the result of their classification.

## Usage examples

In this section, we explain how to run the CSO Classifier to classify a single or multiple (_batch mode_) papers.

### Classifying a single paper (SP)

#### Sample Input (SP)

The sample input can be either a *dictionary* containing title, abstract and keywords as keys, or a *string*:
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

#or

paper = """De-anonymizing Social Networks
Operators of online social networks are increasingly sharing potentially sensitive information about users and their relationships with advertisers, application developers, and data-mining researchers. Privacy is typically protected by anonymization, i.e., removing names, addresses, etc. We present a framework for analyzing privacy and anonymity in social networks and develop a new re-identification algorithm targeting anonymized social-network graphs. To demonstrate its effectiveness on real-world networks, we show that a third of the users who can be verified to have accounts on both Twitter, a popular microblogging service, and Flickr, an online photo-sharing site, can be re-identified in the anonymous Twitter graph with only a 12% error rate. Our de-anonymization algorithm is based purely on the network topology, does not require creation of a large number of dummy "sybil" nodes, is robust to noise and all existing defenses, and works even when the overlap between the target network and the adversary's auxiliary information is small.
data mining, data privacy, graph theory, social networking (online)"""
```

In case the input variable is a *dictionary*, the classifier checks only the fields ```title```, ```abstract``` and ```keywords```. However, there is no need for filling all three of them. Indeed, if for instance you do not have *keywords*, you can just use the *title* and *abstract*.

#### Run (SP)

Just import the classifier and run it:

```python
from cso_classifier import CSOClassifier
cc = CSOClassifier(modules = "both", enhancement = "first", explanation = True)
result = cc.run(paper)
print(result)
```

To observe the available settings please refer to the [Parameters](#parameters) section.

If you have more than one paper to classify, you can use the following example:

```python
from cso_classifier import CSOClassifier
cc = CSOClassifier(modules = "both", enhancement = "first", explanation = True)
results = list()
for paper in papers:
  results.append(cc.run(paper))
print(results)
```

Even if you are running multiple classifications, the current implementation of the CSO Classifier will load the CSO and the model only once, saving computational time.

#### Sample Output (SP)

As output, the classifier returns a dictionary with five components: (i) syntactic, (ii) semantic, (iii) union, (iv) enhanced, and (v) explanation. The latter field is available only if the **explanation** flag is set to True.

Below you can find an example. The keys syntactic and semantic respectively contain the topics returned by the syntacic and semantic module. Union contains the unique topics found by the previous two modules. In ehancement you can find the relevant super-areas. *Please be aware that the results may change according to the version of Computer Science Ontology.*

```json
{
   "syntactic":[
      "network topology",
      "online social networks",
      "real-world networks",
      "anonymization",
      "privacy",
      "social networks",
      "data privacy",
      "graph theory",
      "data mining",
      "sensitive informations",
      "anonymity",
      "micro-blog",
      "twitter"
   ],
   "semantic":[
      "network topology",
      "online social networks",
      "topology",
      "data privacy",
      "social networks",
      "privacy",
      "anonymization",
      "graph theory",
      "data mining",
      "anonymity",
      "micro-blog",
      "twitter"
   ],
   "union":[
      "network topology",
      "online social networks",
      "topology",
      "real-world networks",
      "anonymization",
      "privacy",
      "social networks",
      "data privacy",
      "graph theory",
      "data mining",
      "sensitive informations",
      "anonymity",
      "micro-blog",
      "twitter"
   ],
   "enhanced":[
      "computer networks",
      "online systems",
      "complex networks",
      "privacy preserving",
      "computer security",
      "world wide web",
      "theoretical computer science",
      "computer science",
      "access control",
      "network security",
      "authentication",
      "social media"
   ],
   "explanation":{
		"social networks": ["social network", "online social networks", "microblogging service", "real-world networks", "social networks", "microblogging", "social networking", "twitter graph", "anonymous twitter", "twitter"],
		"online social networks": ["online social networks", "social network", "social networks"],
		"sensitive informations": ["sensitive information"],
		"privacy": ["sensitive information", "anonymity", "anonymous", "data privacy", "privacy"],
		"anonymization": ["anonymization"],
		"anonymity": ["anonymity", "anonymous"],
		"real-world networks": ["real-world networks"],
		"twitter": ["twitter graph", "twitter", "microblogging service", "anonymous twitter", "microblogging"],
		"micro-blog": ["twitter graph", "twitter", "microblogging service", "anonymous twitter", "microblogging"],
		"network topology": ["topology", "network topology"],
		"data mining": ["data mining", "mining"],
		"data privacy": ["data privacy", "privacy"],
		"graph theory": ["graph theory"],
		"topology": ["topology", "network topology"],
		"computer networks": ["topology", "network topology"],
		"online systems": ["online social networks", "social network", "social networks"],
		"complex networks": ["real-world networks"],
		"privacy preserving": ["anonymization"],
		"computer security": ["anonymity", "data privacy", "privacy"],
		"world wide web": ["social network", "online social networks", "microblogging service", "real-world networks", "social networks", "microblogging", "social networking", "twitter graph", "anonymous twitter", "twitter"],
		"theoretical computer science": ["graph theory"],
		"computer science": ["data mining", "mining"],
		"access control": ["sensitive information"],
		"network security": ["anonymity", "sensitive information", "anonymous"],
		"authentication": ["anonymity", "anonymous"],
		"social media": ["microblogging service", "microblogging", "twitter graph", "anonymous twitter", "twitter"]
	}
}
```

### Classifying in batch mode (BM)

#### Sample Input (BM)

The sample input is a *dictionary* of papers. Each key is an identifier (example id1, see below) and its value is either a *dictionary* containing title, abstract and keywords as keys, or a *string*, as shown for [Classifying a single paper (SP)](#classifying-a-single-paper-sp).

```json
papers = {
    "id1": {
        "title": "De-anonymizing Social Networks",
        "abstract": "Operators of online social networks are increasingly sharing potentially sensitive information about users and their relationships with advertisers, application developers, and data-mining researchers. Privacy is typically protected by anonymization, i.e., removing names, addresses, etc. We present a framework for analyzing privacy and anonymity in social networks and develop a new re-identification algorithm targeting anonymized social-network graphs. To demonstrate its effectiveness on real-world networks, we show that a third of the users who can be verified to have accounts on both Twitter, a popular microblogging service, and Flickr, an online photo-sharing site, can be re-identified in the anonymous Twitter graph with only a 12% error rate. Our de-anonymization algorithm is based purely on the network topology, does not require creation of a large number of dummy \"sybil\" nodes, is robust to noise and all existing defenses, and works even when the overlap between the target network and the adversary's auxiliary information is small.",
        "keywords": "data mining, data privacy, graph theory, social networking (online)"
    },
    "id2": {
        "title": "Title of sample paper id2",
        "abstract": "Abstract of sample paper id2",
        "keywords": "keyword1, keyword2, ..., keywordN"
    }
}
```

#### Run (BM)

Import the python script and run the classifier:

```python
from cso_classifier import CSOClassifier
cc = CSOClassifier(workers = 1, modules = "both", enhancement = "first", explanation = True)
result = cc.batch_run(papers)
print(result)
```

To observe the available settings please refer to the [Parameters](#parameters) section.

#### Sample Output (BM)

As output the classifier returns a dictionary of dictionaries. For each classified paper (identified by their id), it returns a dictionary containing five components: (i) syntactic, (ii) semantic, (iii) union, (iv) enhanced, and (v) explanation. The latter field is available only if the explanation flag is set to True.

Below you can find an example. The keys syntactic and semantic respectively contain the topics returned by the syntactic and semantic module. Union contains the unique topics found by the previous two modules. In ehancement you can find the relevant super-areas. In explanation, you can find all chunks of text that allowed the classifier to infer a given topic. *Please be aware that the results may change according to the version of Computer Science Ontology.*

```json
{
    "id1": {
	"syntactic": ["network topology", "online social networks", "real-world networks", "anonymization", "privacy", "social networks", "data privacy", "graph theory", "data mining", "sensitive informations", "anonymity", "micro-blog", "twitter"],
	"semantic": ["network topology", "online social networks", "topology", "data privacy", "social networks", "privacy", "anonymization", "graph theory", "data mining", "anonymity", "micro-blog", "twitter"],
	"union": ["network topology", "online social networks", "topology", "real-world networks", "anonymization", "privacy", "social networks", "data privacy", "graph theory", "data mining", "sensitive informations", "anonymity", "micro-blog", "twitter"],
	"enhanced": ["computer networks", "online systems", "complex networks", "privacy preserving", "computer security", "world wide web", "theoretical computer science", "computer science", "access control", "network security", "authentication", "social media"],
	"explanation": {
		"social networks": ["social network", "online social networks", "microblogging service", "real-world networks", "social networks", "microblogging", "social networking", "twitter graph", "anonymous twitter", "twitter"],
		"online social networks": ["online social networks", "social network", "social networks"],
		"sensitive informations": ["sensitive information"],
		"privacy": ["sensitive information", "anonymity", "anonymous", "data privacy", "privacy"],
		"anonymization": ["anonymization"],
		"anonymity": ["anonymity", "anonymous"],
		"real-world networks": ["real-world networks"],
		"twitter": ["twitter graph", "twitter", "microblogging service", "anonymous twitter", "microblogging"],
		"micro-blog": ["twitter graph", "twitter", "microblogging service", "anonymous twitter", "microblogging"],
		"network topology": ["topology", "network topology"],
		"data mining": ["data mining", "mining"],
		"data privacy": ["data privacy", "privacy"],
		"graph theory": ["graph theory"],
		"topology": ["topology", "network topology"],
		"computer networks": ["topology", "network topology"],
		"online systems": ["online social networks", "social network", "social networks"],
		"complex networks": ["real-world networks"],
		"privacy preserving": ["anonymization"],
		"computer security": ["anonymity", "data privacy", "privacy"],
		"world wide web": ["social network", "online social networks", "microblogging service", "real-world networks", "social networks", "microblogging", "social networking", "twitter graph", "anonymous twitter", "twitter"],
		"theoretical computer science": ["graph theory"],
		"computer science": ["data mining", "mining"],
		"access control": ["sensitive information"],
		"network security": ["anonymity", "sensitive information", "anonymous"],
		"authentication": ["anonymity", "anonymous"],
		"social media": ["microblogging service", "microblogging", "twitter graph", "anonymous twitter", "twitter"]
	    }
    },
    "id2": {
        "syntactic": [...],
        "semantic": [...],
        "union": [...],
        "enhanced": [...],
        "explanation": {...}
    }
}
```

### Parameters
Beside the paper(s), the function running the CSO Classifier accepts seven additional parameters: (i) **workers**, (ii) **modules**, (iii) **enhancement**, (iv) **explanation**, (v) **delete_outliers**, (vi) **fast_classification**, and (vii) **silent**. There is no particular order on how to specify these paramaters. Here we explain their usage. The workers parameters is an integer (equal or greater than 1), modules and enhancement are strings that define a particular behaviour for the classifier. The explanation, delete_outliers, fast_classification, and silent parameters are booleans.

(i) The parameter *workers* defines the number of threads to run for classifying the input corpus. For instance, if ```workers = 4```, there will be 4 instances of the CSO Classifier, each one receiving a chunk (equally split) of the corpus to process. Once all processes are completed, the results will be aggregated and returned. The default value for *workers* is *1*. This parameter is available only when running the classifier in *batch mode*.

(ii) The parameter *modules* can be either "syntactic", "semantic", or "both". Using the value "syntactic", the classifier will run only the syntactic module. Using the "semantic" value, instead, the classifier will use only the semantic module. Finally, using "both", the classifier will run both syntactic and semantic modules and combine their results. The default value for *modules* is *both*.

(iii) The parameter *enhancement* can be either "first", "all", or "no". This parameter controls whether the classifier will try to infer, given a topic (e.g., Linked Data), only the direct super-topics (e.g., Semantic Web) or all its super-topics (e.g., Semantic Web, WWW, Computer Science). Using "first" as a value will infer only the direct super topics. Instead, if using "all", the classifier will infer all its super-topics. Using "no" the classifier will not perform any enhancement. The default value for *enhancement* is *first*.

(iv) The parameter *explanation* can be either *True* or *False*. This parameter defines whether the classifier should return an explanation. This explanation consists of chunks of text, coming from the input paper, that allowed the classifier to return a given topic. This supports the user in better understanding why a certain topic has been inferred. The classifier will return an explanation for all topics, even for the enhanced ones. In this case, it will join all the text chunks of all its sub-topics. The default value for *explanation* is *False*.

(v) The parameter *delete_outliers* can be either *True* or *False*. This parameter controls whether to run the outlier detection component within the post-processing module. This component improves the results by removing erroneous topics that were conceptually distant from the others. Due to their computation, users might experience slowdowns. For this reason, users can decide between good results and low computational time or improved results and slower computation. The default value for *delete_outliers* is *True*.

(vi) The parameter *fast_classification* can be either *True* or *False*. This parameter determines whether the semantic module should use the full model or the cached one. Using the full model provides slightly better results than the cached one. However, using the cached model is more than 15x faster. Read [here](#word2vec-model-and-token-to-cso-combined-file-generation) for more details about these two models. The default value for *fast_classification* is *True*.

(vii) The parameter *silent* can be either *True* or *False*. This determines whether the classifier prints its progress in the console. If set to True, the classifier will be silent and will not print any output while classifying. The default value for *silent* is *False*.


|# | Parameter  |  Single Paper | Batch Mode |
|---|---|---|---|
|i  | workers  | :x:  | :white_check_mark: |
|ii | modules  | :white_check_mark:  | :white_check_mark: |
|iii| enhancement  | :white_check_mark:  | :white_check_mark: |
|iv | explanation  | :white_check_mark:  | :white_check_mark: |
|v  |delete_outliers| :white_check_mark:  | :white_check_mark: |
|vi | fast_classification| :white_check_mark:  | :white_check_mark: |
|vii| silent       | :white_check_mark:  | :white_check_mark: |

**Table 1**: Parameters availability when using CSO Classifier


## Releases

Here we list the available releases for the CSO Classifier. These releases are available for download both from [Github](https://github.com/angelosalatino/cso-classifier/releases) and [Zenodo](10.5281/zenodo.2660819).

### v3.0

This release welcomes some improvements under the hood. In particular:
* we refactored the code, reorganising scripts into more elegant classes
* we added functionalities to automatically setup and update the classifier to the latest version of CSO
* we added the *explanation* feature, which returns chunks of text that allowed the classifier to infer a given topic
* the syntactic module takes now advantage of Spacy POS tagger (as previously done only by semantic module)
* the grammar for the chunk parser is now more robust: ```{<JJ.*>*<HYPH>*<JJ.*>*<HYPH>*<NN.*>*<HYPH>*<NN.*>+}```

In addition, in the post-processing module, we added the *outlier detection* component. This component improves the accuracy of the result set, by removing erroneous topics that were conceptually distant from the others. This component is enabled by default and can be disabled by setting ```delete_outliers = False``` when calling the CSO Classifier (see [Parameters](#parameters)).

Please, be aware that having substantially restructured the code into classes, the way of running the classifier has changed too. Thus, if you are using a previous version of the classifier, we encourage you to update it (```pip install -U cso-classifier```) and modify your calls to the classifier, accordingly. Read our [usage examples](#usage-examples).

We would like to thank James Dunham @jamesdunham from CSET (Georgetown University) for suggesting to us how to improve the code.

Download from:

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5095422.svg)](https://doi.org/10.5281/zenodo.5095422)

### v2.3.2

Version alignement with Pypi. Similar to version 2.3.1.

Download from:

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3357768.svg)](https://doi.org/10.5281/zenodo.3357768)


### v2.3.1

Bug Fix. Added some exception handles. 
**Notice:** *Please note that during the upload of this version on Pypi (python index), we encountered some issues. We can't guarantee this version will work properly. To this end, we created a new release: v2.3.2. Use this last one, please. Apologies for any inconvenience.*

### v2.3
This new release contains a bug fix and the latest version of the CSO ontology.

Bug Fix: When running in batch mode, the classifier was treating the keyword field as an array instead of a string. In this way, instead of processing keywords (separated by comma), it was processing each single letters, hence inferring wrong topics. This now has been fixed. In addition, if the keyword field is actually an array, the classifier will first 'stringify' it and then process it.

We also downloaded and packed the latest version of the CSO ontology.

Download from:

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3355629.svg)](https://doi.org/10.5281/zenodo.3355629)

### v2.2
In this version (release v2.2), we (i) updated the requirements needed to run the classifier, (ii) removed all unnecessary warnings, and (iii) enabled multiprocessing. In particular, we removed all useless requirements that were installed in development mode, by cleaning the _requirements.txt_ file. 

When computing certain research papers, the classifier display warnings raised by the [kneed library](https://pypi.org/project/kneed/). Since the classifier can automatically adapt to such warnings, we decided to hide them and prevent users from being concerned about such an outcome.

This version of the classifier provides improved **scalability** through multiprocessing. Once the number of workers is set (i.e. num_workers >= 1), each worker will be given a copy of the CSO Classifier with a chunk of the corpus to process. Then, the results will be aggregated once all processes are completed. Please be aware that this function is only available in batch mode. See section [Classifying in batch mode (BM)](#classifying-in-batch-mode-bm) for more details.

Download from:

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3241490.svg)](https://doi.org/10.5281/zenodo.3241490)

### v2.1
This new release (version v2.1) makes the CSO Classifier more scalable. Compared to its previous version (v2.0), the classifier relies on a cached word2vec model which connects the words within the model vocabulary directly with the CSO topics. Thanks to this cache, the classifier is able to quickly retrieve all CSO topics that could be inferred by given tokens, speeding up the processing time. In addition, this cache is lighter (~64M) compared to the actual word2vec model (~366MB), which allows saving additional time at loading time.

Thanks to this improvement the CSO Classifier is around 24x faster and can be easily run on a large corpus of scholarly data.

Download from:

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.2689440.svg)](https://doi.org/10.5281/zenodo.2689440)

### v2.0

The second version (v2.0) implements the CSO Classifier as described in the [about section](#about). It combines the topics of both the syntactic and semantic modules and enriches them with their super-topics. Compared to [v1.0](#v10), it adds a semantic layer that allows generating a more comprehensive result, identifying research topics that are not explicitly available in the metadata. The semantic module relies on a Word2vec model trained on over 4.5M papers in _Computer Science_. [Below](#word-embedding-generation) we show more in detail how we trained such a model. In this version of the classifier, we [pickled](https://docs.python.org/3.6/library/pickle.html) the model to speed up the process of loading into memory (~4.5 times faster).

> Salatino, A.A., Osborne, F., Thanapalasingam, T., Motta, E.: The CSO Classifier: Ontology-Driven Detection of Research Topics in Scholarly Articles. In: TPDL 2019: 23rd International Conference on Theory and Practice of Digital Libraries. Springer. [Read More](http://oro.open.ac.uk/62026/)

Download from:

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.2661834.svg)](https://doi.org/10.5281/zenodo.2661834)

### v1.0

The first version (v1.0) of the CSO Classifier is an implementation of the syntactic module, which was also previously used to support the semi-automatic annotation of proceedings at Springer Nature [[1]](#references). This classifier aims at syntactically match n-grams (unigrams, bigrams and trigrams) of the input document with concepts within CSO.

More details about this version of the classifier can be found within: 
> Salatino, A.A., Thanapalasingam, T., Mannocci, A., Osborne, F. and Motta, E. 2018. Classifying Research Papers with the Computer Science Ontology. ISWC-P&D-Industry-BlueSky 2018 (2018). [Read more](http://oro.open.ac.uk/55908/)

Download from:

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.2661834.svg)](https://doi.org/10.5281/zenodo.2661834)

## List of Files

* **CSO-Classifier.ipynb**: :page_facing_up: Python notebook for executing the classifier
* **CSO-Classifier.py**: :page_facing_up: Python script for executing the classifier
* **images**: :file_folder: folder containing some pictures, e.g., the workflow showed above
* **cso_classifier**: :file_folder: Folder containing the main functionalities of the classifier
  * **classifier.py**: :page_facing_up: class that implements the CSO Classifier
  * **syntacticmodule.py**: :page_facing_up: class that implements the syntactic module
  * **semanticmodule.py**: :page_facing_up: class that implements the semantic module
  * **postprocmodule.py**: :page_facing_up:
  * **paper.py**: :page_facing_up: class that implements the functionalities to operate on papers, such as POS tagger, grammar-based chunk parser
  * **result.py**: :page_facing_up: class that implements the functionality to operate on the results
  * **ontology.py**: :page_facing_up: class that implements the functionalities to operate on the ontology: get primary label, get topics and so on
  * **model.py**: :page_facing_up: class that implements the functionalities to operate on the word2vec model: get similar words and so on
  * **misc.py**: :page_facing_up: some miscellaneous functionalities
  * **test.py**: :page_facing_up: some test functionalities
  * **config.py**: :page_facing_up: class that implements the functionalities to operate on the config file
  * **config.ini**: :page_facing_up: config file. It contains all information about packaage, ontology and model.
  * **assets**: :file_folder: Folder containing the word2vec model and CSO
    * **cso.csv**: :page_facing_up: file containing the Computer Science Ontology in csv
    * **cso.p**: :page_facing_up: serialised file containing the Computer Science Ontology (pickled)
    * **cso_graph.p** :page_facing_up: file containing the Computer Science Ontology as an iGraph object
    * **model.p**: :page_facing_up: the trained word2vec model (pickled)
    * **token-to-cso-combined.json**: :page_facing_up: file containing the cached word2vec model. This json file contains a dictionary in which each token of the corpus vocabulary, has been mapped with the corresponding CSO topics. Below we explain how this file has been generated.

## Word2vec model and token-to-cso-combined file generation

In this section, we describe how we generated the word2vec model used within the CSO Classifier and what is the token-to-cso-combined file.

### Word Embedding generation

We applied the word2vec approach [[2,3]](#references) to a collection of text from the Microsoft Academic Graph (MAG) for generating word embeddings. MAG is a scientific knowledge base and a heterogeneous graph containing scientific publication records, citation relationships, authors, institutions, journals, conferences, and fields of study. It is the largest dataset of scholarly data publicly available, and, as of April 2021, it contains more than 250 million publications.

We first downloaded titles, and abstracts of 4,654,062 English papers in the field of Computer Science. Then we pre-processed the data by replacing spaces with underscores in all n-grams matching the CSO topic labels (e.g., “digital libraries” became “digital_libraries”) and for frequent bigrams and trigrams (e.g., “highest_accuracies”, “highly_cited_journals”). These frequent n-grams were identified by analysing combinations of words that co-occur together, as suggested in [[2]](#references) and using the parameters showed in Table 2. Indeed, while it is possible to obtain the vector of an n-gram by averaging the embedding vectors of all its words, the resulting representation usually is not as good as the one obtained by considering the n-gram as a single word during the training phase.

Finally, we trained the word2vec model using the parameters provided in Table 3. The parameters were set to these values after testing several combinations.

| min-count  |  threshold |
|---|---|
| 5  | 10  |

**Table 2**: Parameters used during the collocation words analysis


| method  |  emb. size | window size | min count cutoff |
|---|---|---|---|
| skipgram  | 128  |  10 |  10 |

**Table 3**: Parameters used for training the word2vec model.


After training the model, we obtained a **gensim.models.keyedvectors.Word2VecKeyedVectors** object weighing **366MB**. You can download the model [from here](https://cso.kmi.open.ac.uk/download/model.p).

The size of the model hindered the performance of the classifier in two ways. Firstly, it required several seconds to be loaded into memory. This was partially fixed by serialising the model file (using python pickle, see version v2.0 of CSO Classifier, ~4.5x faster). Secondly, while processing a document, the classifier needs to retrieve the top 10 similar words for all tokens, and compare them with CSO topics. In performing such an operation, the model would require several seconds, becoming a bottleneck for the classification process.

To this end, we decided to create a cached model (**token-to-cso-combined.json**) which is a dictionary that directly connects all token available in the vocabulary of the model with the CSO topics. This strategy allows to quickly retrieve all CSO topics that can be inferred by a particular token.

### token-to-cso-combined file

To generate this file, we collected all the set of words available within the vocabulary of the model. Then iterating on each word, we retrieved its top 10 similar words from the model, and we computed their Levenshtein similarity against all CSO topics. If the similarity was above 0.7, we created a record that stored all CSO topics triggered by the initial word.

## Use the CSO Classifier in other domains of Science

In order to use the CSO Classifier in other domains of Science, it is necessary to replace the two external sources mentioned in the previous section. In particular, there is a need for a comprehensive ontology or taxonomy of research areas, within the new domain, which will work as a controlled list of research topics. In addition, it is important to train a new word2vec model that fits the language model and the semantic of the terms, in this particular domain. We wrote a blog article on how to integrate knowledge from other fields of Science within the CSO Classifier.

Please read here for more info: [How to use the CSO Classifier in other domains](https://salatino.org/wp/how-to-use-the-cso-classifier-in-other-domains/)

## How to Cite CSO Classifier

We kindly ask that any published research making use of the CSO Classifier cites our paper listed below:

Salatino, A.A., Osborne, F., Thanapalasingam, T., Motta, E.: The CSO Classifier: Ontology-Driven Detection of Research Topics in Scholarly Articles. In: TPDL 2019: 23rd International Conference on Theory and Practice of Digital Libraries. Springer.

## License

[Apache 2.0](https://choosealicense.com/licenses/apache-2.0/)

## References

[1] Osborne, F., Salatino, A., Birukou, A. and Motta, E. 2016. Automatic Classification of Springer Nature Proceedings with Smart Topic Miner. The Semantic Web -- ISWC 2016. 9982 LNCS, (2016), 383–399. DOI:https://doi.org/10.1007/978-3-319-46547-0_33

[2] Mikolov, T., Chen, K., Corrado, G. and Dean, J. 2013. Efficient Estimation of Word Representations in Vector Space. (Jan. 2013).

[3] Mikolov, T., Chen, K., Corrado, G. and Dean, J. 2013. Distributed Representations of Words and Phrases and their Compositionality. Advances in neural information processing systems. 3111–3119.
