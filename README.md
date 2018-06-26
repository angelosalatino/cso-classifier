# CSO-Classifier

Script that classifes content from scientific papers with the topics of the [Computer Science Ontology (CSO)](https://cso.kmi.open.ac.uk). Being able to synthesize the content of papers, allows to perform different kinds of analytics:
* Trend analysis
* Recommender systems
* Find authors’ topics of interest
* Topic analysis


## About

If you use the CSO classfier in your research or work and would like to cite the SKM3 Application Programming Interface, we suggest you cite the [CSO portal paper](http://skm.kmi.open.ac.uk/the-computer-science-ontology-a-large-scale-taxonomy-of-research-areas/).

## Framework
![Framework of CSO Classifier](/pics/framework.png "Framework of CSO Classifier")

## Requirements
1. Ensure you have [**Python 3**](https://www.python.org/downloads/) installed.
2. Install the necessary depepencies by executing the following command:```pip install -r requirements.txt```
3. Download NLP datasets by running the following line  within your Python 3 interpreter: ```import nltk; nltk.download('stopwords');```

## In depth
1. The algorithm firstly preprocesses the content of each paper: removes punctuation and stop words.
2. Then, it parses the text to find n-grams (unigram, bigrams and trigrams) that match, with a certain degree of similarity (default: Levenshtein >= 0.85), with the topics within the Computer Science Ontology.
3. Thirdly, it adds more broader generic topics, based on the ones retrieved in Step 2. It exploits the _skos:broaderGeneric_ relationships within the CSO. A more broader topic is included if a certain amount of narrower topics (default: num_narrower = 2) are in the initial set of topics. The selcgtion of more broader generic topics can be achieved in two ways:
  * select just the first broader topic, or in other words the direct broaders of the topics extracted from the paper;
  * select the whole tree from the first broader topic up until the root of the ontology.
4. Lastly, it cleans the output removing statistic values, and removes similar topics using the _relatedEquivalent_ within the CSO.

## Choosing the Ontology
In the repository you can find two versions of the CSO (_ComputerScienceOntology.csv_):

```python
# Version 1: 15K topics and 90K relationships
clf = CSO(version=1)
```
or
```python
# Version 2: 26K topics and 226K relationships
clf = CSO(version=2)
```


## Instance
Input:
```json
paper = {"title": "Detection of Embryonic Research Topics by Analysing Semantic Topic Networks",
         "abstract": "Being aware of new research topics is an important asset for anybody involved in the research environment, including researchers, academic publishers and institutional funding bodies. In recent years, the amount of scholarly data available on the web has increased steadily, allowing the development of several approaches for detecting emerging research topics and assessing their trends. However, current methods focus on the detection of topics which are already associated with a label or a substantial number of documents. In this paper, we address instead the issue of detecting embryonic topics, which do not possess these characteristics yet. We suggest that it is possible to forecast the emergence of novel research topics even at such early stage and demonstrate that the emergence of a new topic can be anticipated by analysing the dynamics of pre-existing topics. We present an approach to evaluate such dynamics and an experiment on a sample of 3 million research papers, which confirms our hypothesis. In particular, we found that the pace of collaboration in sub-graphs of topics that will give rise to novel topics is significantly higher than the one in the control group.",
         "keywords": "Scholarly Data, Research Trend Detection, Topic Emergence Detection, Topic Discovery, Semantic Web, Ontology"
        }
```

Running the classifier:
```python
# cso is a dictionary loaded beforehand
# num_narrower = 1, include all the broader topics having at least one narrower topic matched in the paper
# min_similarity = 0.9, more precise similarity between n-grams and topics has been requested
# climb_ont = 'jfb', it adds 'just the first broader topic'. The other option available is 'wt' as it adds the whole tree up until the root. 
# verbose = True, it returns the result in a verbose way. It reports the different statistics associated with matches.
result = clf.classify(PAPER, format='json', num_narrower=1, min_similarity=0.9, climb_ont='jfp', verbose=True)
print(json.dumps(result))
```
Result (variable **_result_**):
```json
{  
   "semantics":[  
      {  
         "matched":"semantic",
         "similarity":0.9411764705882353
      },
      {  
         "matched":"semantic",
         "similarity":0.9411764705882353
      },
      {  
         "matched":2,
         "broader of":[  
            "ontology",
            "semantic web"
         ]
      }
   ],
   "semantic":[  
      {  
         "matched":"semantic",
         "similarity":1.0
      },
      {  
         "matched":"semantic",
         "similarity":1.0
      },
      {  
         "matched":2,
         "broader of":[  
            "ontology",
            "semantic web"
         ]
      }
   ],
   "ontology":[  
      {  
         "matched":"ontology",
         "similarity":1.0
      }
   ],
   "semantic web":[  
      {  
         "matched":"semantic web",
         "similarity":1.0
      }
   ],
   "world wide web":[  
      {  
         "matched":1,
         "broader of":[  
            "semantic web"
         ]
      }
   ]
}
```

and then cleaning the result:
```python
result = clf.classify(PAPER, format='json', num_narrower=1, min_similarity=0.9, climb_ont='jfp', verbose=False)
print(json.dumps(result))
```

List of final topics (variable **_result_**):
```json
[  
   "ontology-based",
   "semantic web technologies",
   "semantics",
   "world wide web"
]
```
