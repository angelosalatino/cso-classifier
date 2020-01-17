import math
from functools import partial
from multiprocessing.pool import Pool

from classifier import misc
from classifier.semanticmodule import Semantic as sema
from classifier.syntacticmodule import Syntactic as synt
from classifier.ontology import Ontology as CSO
from classifier.model import Model as MODEL
from classifier.paper import Paper
from classifier.result import Result
from classifier.config import Config


def run_cso_classifier(paper, modules="both", enhancement="first", explanation=False):
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
        explanation (boolean): if true it returns the chunks of text that allowed to infer a particular topic. This feature
        of the classifier is useful as it allows users to asses the result

    Returns:
        class_res (dictionary): containing teh result of each classification
    """

    if modules not in ["syntactic", "semantic", "both"]:
        raise ValueError("Error: Field modules must be 'syntactic', 'semantic' or 'both'")

    if enhancement not in ["first", "all", "no"]:
        raise ValueError("Error: Field enhances must be 'first', 'all' or 'no'")
    
    if type(explanation) != bool:
        raise ValueError("Error: Explanation must be set to either True or False")

    
    # Loading ontology and model
    cso = CSO()
    model = MODEL()
    t_paper = Paper(paper, modules)
    result = Result(explanation)

    # Passing parameters to the two classes (synt and sema) and actioning classifiers

    if modules == 'syntactic' or modules == 'both':
        synt_module = synt(cso, t_paper)
        result.set_syntactic(synt_module.classify_syntactic())
        if explanation: result.dump_temporary_explanation(synt_module.get_explanation())
    if modules == 'semantic' or modules == 'both':
        sema_module = sema(model, cso, t_paper)
        result.set_semantic(sema_module.classify_semantic())
        if explanation: result.dump_temporary_explanation(sema_module.get_explanation())
       
    result.set_enhanced(cso.climb_ontology(getattr(result, "union"), enhancement))


    return result.get_dict()


def run_cso_classifier_batch_model_single_worker(papers, modules="both", enhancement="first", explanation = False):
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
        explanation (boolean): if true it returns the chunks of text that allowed to infer a particular topic. This feature
        of the classifier is useful as it allows users to asses the result

    Returns:
        class_res (dictionary): containing teh result of each classification
    """

    if modules not in ["syntactic", "semantic", "both"]:
        raise ValueError("Error: Field modules must be 'syntactic', 'semantic' or 'both'")

    if enhancement not in ["first", "all", "no"]:
        raise ValueError("Error: Field enhances must be 'first', 'all' or 'no'")
    
    if type(explanation) != bool:
        raise ValueError("Error: Explanation must be set to either True or False")

    # Loading ontology and model
    cso = CSO()
    model = MODEL()
    paper = Paper(modules = modules)
    
    

    # Passing parameters to the two classes (synt and sema)
    synt_module = synt(cso)
    sema_module = sema(model, cso)

    # initializing variable that will contain output
    class_res = dict()

    for paper_id, paper_value in papers.items():
        print("Processing:", paper_id)

        paper.set_paper(paper_value)
        result = Result()

        # Passing paper and actioning the classifier    
        if modules == 'syntactic' or modules == 'both':
            synt_module.set_paper(paper)
            result.set_syntactic(synt_module.classify_syntactic())
        if modules == 'semantic' or modules == 'both':
            sema_module.set_paper(paper)
            result.set_semantic(sema_module.classify_semantic())
           
        result.set_enhanced(cso.climb_ontology(getattr(result, "union"), enhancement))
        
        class_res[paper_id] = result.get_dict()

    return class_res




def run_cso_classifier_batch_mode(papers, workers=1, modules="both", enhancement="first", explanation = False):
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
        explanation (boolean): if true it returns the chunks of text that allowed to infer a particular topic. This feature
        of the classifier is useful as it allows users to asses the result

    Returns:
        class_res (dictionary): containing teh result of each classification
    """

    if modules not in ["syntactic", "semantic", "both"]:
        raise ValueError("Error: Field modules must be 'syntactic', 'semantic' or 'both'")

    if enhancement not in ["first", "all", "no"]:
        raise ValueError("Error: Field enhances must be 'first', 'all' or 'no'")
    
    if type(workers) != int:
        raise ValueError("Error: Number of workers must be integer")

    if workers < 1:
        raise ValueError("Error: Number of workers must be equal or greater than 1")
    
    if type(explanation) != bool:
        raise ValueError("Error: Explanation must be set to either True or False")
    


    size_of_corpus = len(papers)
    chunk_size = math.ceil(size_of_corpus / workers)
    papers_list = list(misc.chunks(papers, chunk_size))
    annotate = partial(run_cso_classifier_batch_model_single_worker, modules=modules, enhancement=enhancement)

    with Pool(workers) as p:
        result = p.map(annotate, papers_list)

    class_res = {k: v for d in result for k, v in d.items()}

    return class_res



def setup():
    """ Setting up the classifier: language model, ontology and word2vec model
    """
    misc.download_language_model()
    
    cso = CSO(load_ontology = False)
    cso.setup()
    
    model = MODEL(load_model = False)
    model.setup()
    

def update(force = False):
    """ Update the ontology and the word2vec model
    """
    cso = CSO(load_ontology = False)
    cso.update(force = force)
    
    model = MODEL(load_model = False)
    model.update(force = force)
    

def version():
    """ Function that returns the version number of different components: classifier and ontology
    """
    config = Config()
    misc.print_header("CLASSIFIER")
    print("CSO Classifier version {}".format(config.get_classifier_version()))

    import subprocess   
    import sys
    
    latest_version = str(subprocess.run([sys.executable, '-m', 'pip', 'install', '{}==random'.format(config.get_package_name())], capture_output=True, text=True))
    latest_version = latest_version[latest_version.find('(from versions:')+15:]
    latest_version = latest_version[:latest_version.find(')')]
    latest_version = latest_version.replace(' ','').split(',')[-1]
    
    if latest_version > config.get_classifier_version():
        print("A more recent version ({}) of the CSO Classifier is available.".format(latest_version))
        print("You can update this package by running: pip install cso-classifier -U")
    elif latest_version == config.get_classifier_version():
        print("The version of the CSO Classifier you are using is already up to date.")
    elif latest_version < config.get_classifier_version():
        print("The latest available package is version {} and you are using version {}. There is an error in your configuration file.".format(latest_version,config.get_classifier_version()))
    
    cso = CSO(load_ontology = False)
    cso.version()
    