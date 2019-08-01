#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  7 17:19:22 2019

@author: angelosalatino
"""



import math
from functools import partial
from multiprocessing.pool import Pool

from classifier import misc
from classifier.semanticmodule import CSOClassifierSemantic as sema
from classifier.syntacticmodule import CSOClassifierSyntactic as synt


def run_cso_classifier(paper, modules="both", enhancement="first"):
    """Run the CSO Classifier.

    It takes as input the text from abstract, title, and keywords of a research paper and outputs a list of relevant
    concepts from CSO.

    This function requires the paper (please note, one single paper, no batch mode) and few flags: 
        (i) modules, determines whether to run only the syntactic module, or the semantic module, or both;
        (ii) enhancement, controls whether the classifier should infer super-topics, i.e., their first direct
        super-topics or the whole set of topics up until root.

    Args:
        paper (dictionary): contains the metadata of the paper, e.g., title, abstract and keywords {"title": "",
        "abstract": "","keywords": ""}.
        modules (string): either "syntactic", "semantic" or "both" to determine which modules to use when
        classifying. "syntactic" enables only the syntactic module. "semantic" enables only the semantic module.
        Finally, with "both" the classifier takes advantage of both the syntactic and semantic modules. Default =
        "both".
        enhancement (string): either "first", "all" or "no". With "first" the CSO classifier returns only the topics
        one level above. With "all" it returns all topics above the resulting topics. With "no" the CSO Classifier
        does not provide any enhancement.

    Returns:
        fcso (dictionary): contains the CSO Ontology.
        fmodel (dictionary): contains a cache of the model, i.e., each token is linked to the corresponding CSO topic.
    """

    if modules not in ["syntactic", "semantic", "both"]:
        raise ValueError("Error: Field modules must be 'syntactic', 'semantic' or 'both'")

    if enhancement not in ["first", "all", "no"]:
        raise ValueError("Error: Field enhances must be 'first', 'all' or 'no'")

    # Loading ontology and model
    cso, model = misc.load_ontology_and_chached_model()

    # Passing parameters to the two classes (synt and sema)
    synt_module = synt(cso, paper)
    sema_module = sema(model, cso, paper)

    # initializing variable that will contain output
    class_res = dict()
    class_res["syntactic"] = list()
    class_res["semantic"] = list()
    class_res["union"] = list()
    class_res["enhanced"] = list()

    if modules == 'syntactic' or modules == 'both':
        class_res["syntactic"] = synt_module.classify_syntactic()
    if modules == 'semantic' or modules == 'both':
        class_res["semantic"] = sema_module.classify_semantic()

    union = list(set(class_res["syntactic"] + class_res["semantic"]))
    class_res["union"] = union

    if enhancement == 'first':
        enhanced = misc.climb_ontology(cso, union, "first")
        class_res["enhanced"] = [x for x in enhanced if x not in union]
    elif enhancement == 'all':
        enhanced = misc.climb_ontology(cso, union, "all")
        class_res["enhanced"] = [x for x in enhanced if x not in union]
    elif enhancement == 'no':
        pass

    return class_res


def run_cso_classifier_batch_mode(papers, workers=1, modules="both", enhancement="first"):
    """Run the CSO Classifier in *BATCH MODE* and with multiprocessing.

    It takes as input a set of papers, which include abstract, title, and keywords and for each one of them returns a
    list of relevant concepts from CSO. This function requires a dictionary of papers, with each id corresponding to
    the metadata of a paper, and few flags: (i) modules, determines whether to run only the syntactic module,
    or the semantic module, or both; (ii) enhancement, controls whether the classifier should infer super-topics,
    i.e., their first direct super-topics or the whole set of topics up until root.

    Args:
        papers (dictionary): contains the metadata of the papers, e.g., for each paper, there is title, abstract and
        keywords {"id1":{"title": "","abstract": "","keywords": ""},"id2":{"title": "","abstract": "","keywords": ""}}.
        workers (integer): number of workers. If 1 is in single thread, otherwise multithreaded
        modules (string): either "syntactic", "semantic" or "both" to determine which modules to use when
        classifying. "syntactic" enables only the syntactic module. "semantic" enables only the semantic module.
        Finally, with "both" the classifier takes advantage of both the syntactic and semantic modules. Default =
        "both".
        enhancement (string): either "first", "all" or "no". With "first" the CSO classifier returns only the topics
        one level above. With "all" it returns all topics above the resulting topics. With "no" the CSO Classifier
        does not provide any enhancement.

    Returns:
        fcso (dictionary): contains the CSO Ontology.
        fmodel (dictionary): contains a cache of the model, i.e., each token is linked to the corresponding CSO topic.
    """

    if modules not in ["syntactic", "semantic", "both"]:
        raise ValueError("Error: Field modules must be 'syntactic', 'semantic' or 'both'")

    if enhancement not in ["first", "all", "no"]:
        raise ValueError("Error: Field enhances must be 'first', 'all' or 'no'")

    if workers < 1:
        raise ValueError("Error: Number of workers must be equal or greater than 1")

    if type(workers) != int:
        raise ValueError("Error: Number of workers must be integer")

    size_of_corpus = len(papers)
    chunk_size = math.ceil(size_of_corpus / workers)
    papers_list = list(misc.chunks(papers, chunk_size))
    annotate = partial(run_cso_classifier_batch_model_single_worker, modules=modules, enhancement=enhancement)

    with Pool(workers) as p:
        result = p.map(annotate, papers_list)

    class_res = {k: v for d in result for k, v in d.items()}

    return class_res


def run_cso_classifier_batch_model_single_worker(papers, modules="both", enhancement="first"):
    """Run the CSO Classifier in *BATCH MODE*.

    It takes as input a set of papers, which include abstract, title, and keywords and for each one of them returns a
    list of relevant concepts from CSO. This function requires a dictionary of papers, with each id corresponding to
    the metadata of a paper, and few flags:
    (i) modules, determines whether to run only the syntactic module, or the semantic module, or both;
    (ii) enhancement, controls whether the classifier should infer super-topics, i.e., their first direct
    super-topics or the whole set of topics up until root.
    

    Args:
        papers (dictionary): contains the metadata of the papers, e.g., for each paper, there is title, abstract and
        keywords {"id1":{"title": "","abstract": "","keywords": ""},"id2":{"title": "","abstract": "","keywords": ""}}.
        modules (string): either "syntactic", "semantic" or "both" to determine which modules to use when
        classifying. "syntactic" enables only the syntatcic module. "semantic" enables only the semantic module.
        Finally, with "both" the classifier takes advantage of both the syntactic and semantic modules. Default =
        "both".
        enhancement (string): either "first", "all" or "no". With "first" the CSO classifier returns only the topics
        one level above. With "all" it returns all topics above the resulting topics. With "no" the CSO Classifier
        does not provide any enhancement.

    Returns:
        fcso (dictionary): contains the CSO Ontology.
        fmodel (dictionary): contains a cache of the model, i.e., each token is linked to the corresponding CSO topic.
    """

    if modules not in ["syntactic", "semantic", "both"]:
        raise ValueError("Error: Field modules must be 'syntactic', 'semantic' or 'both'")

    if enhancement not in ["first", "all", "no"]:
        raise ValueError("Error: Field enhances must be 'first', 'all' or 'no'")

    # Loading ontology and model
    cso, model = misc.load_ontology_and_chached_model()

    # Passing parameters to the two classes (synt and sema)
    synt_module = synt(cso)
    sema_module = sema(model, cso)

    # initializing variable that will contain output
    class_res = dict()

    for paper_id, paper_value in papers.items():
        print("Processing:", paper_id)

        # In this case we avoid computing other fields. We select only title, abstract and keywords
        paper = dict()
            
        paper["title"] = paper_value["title"] if "title" in paper_value and not paper_value["title"] is None else ""
        paper["abstract"] = paper_value["abstract"] if "abstract" in paper_value and not paper_value["abstract"] is None else ""
        paper["keywords"] = paper_value["keywords"] if "keywords" in paper_value and not paper_value["keywords"] is None else ""
        #just in case the value keywords contains an array of keywords
        if isinstance(paper["keywords"], list):
            paper["keywords"] = ', '.join(paper["keywords"])

        class_res[paper_id] = dict()
        class_res[paper_id]["syntactic"] = list()
        class_res[paper_id]["semantic"] = list()
        class_res[paper_id]["union"] = list()
        class_res[paper_id]["enhanced"] = list()

        if modules == 'syntactic' or modules == 'both':
            synt_module.set_paper(paper)
            class_res[paper_id]["syntactic"] = synt_module.classify_syntactic()
        if modules == 'semantic' or modules == 'both':
            sema_module.set_paper(paper)
            class_res[paper_id]["semantic"] = sema_module.classify_semantic()

        union = list(set(class_res[paper_id]["syntactic"] + class_res[paper_id]["semantic"]))
        class_res[paper_id]["union"] = union

        if enhancement == 'first':
            enhanced = misc.climb_ontology(cso, union, "first")
            class_res[paper_id]["enhanced"] = [x for x in enhanced if x not in union]
        elif enhancement == 'all':
            enhanced = misc.climb_ontology(cso, union, "all")
            class_res[paper_id]["enhanced"] = [x for x in enhanced if x not in union]
        elif enhancement == 'no':
            pass

    return class_res