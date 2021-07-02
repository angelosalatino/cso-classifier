import math
from functools import partial
from multiprocessing.pool import Pool
from update_checker import UpdateChecker

from .misc import chunks, download_language_model, print_header
from .semanticmodule import Semantic as sema
from .syntacticmodule import Syntactic as synt
from .postprocmodule import PostProcess as post
from .ontology import Ontology as CSO
from .model import Model as MODEL
from .paper import Paper
from .result import Result
from .config import Config



class CSOClassifier:
    """ A simple abstraction layer implementing the CSO Classifier """

    def __init__(self, **parameters):
        """ Initialising the classifier class


        Args:
            - modules (string): either "syntactic", "semantic" or "both" to determine which modules to use when
                    classifying. "syntactic" enables only the syntactic module. "semantic" enables only the semantic module.
                    Finally, with "both" the classifier takes advantage of both the syntactic and semantic modules. Default =
                    "both".
            - enhancement (string): either "first", "all" or "no". With "first" the CSO classifier returns only the topics
                    one level above. With "all" it returns all topics above the resulting topics. With "no" the CSO Classifier
                    does not provide any enhancement.
            - explanation (boolean): if true it returns the chunks of text that allowed to infer a particular topic. This feature
                    of the classifier is useful as it allows users to asses the result.
            - delete_outliers (boolean): if True it runs the outlier detection approach in the postprocessing
            - fast_classification (boolen): if True it runs the fast version of the classifier (cached model).
                    If False the classifier uses the word2vec model which has higher computational complexity
            - silent (boolean): determines whether to print the progress. If true goes in silent mode.
                    Instead, if false does not print anything in standard output.

        """
        self.modules             = parameters["modules"] if "modules" in parameters else "both"
        self.enhancement         = parameters["enhancement"] if "enhancement" in parameters else "first"
        self.explanation         = parameters["explanation"] if "explanation" in parameters else False
        self.delete_outliers     = parameters["delete_outliers"] if "delete_outliers" in parameters else True
        self.fast_classification = parameters["fast_classification"] if "fast_classification" in parameters else True
        self.silent              = parameters["silent"] if "silent" in parameters else False

        self.__check_parameters(parameters)

        self.use_full_model = self.delete_outliers or not self.fast_classification

        self.models_loaded = False
        self.cso = None
        self.model = None



    def run(self, paper):
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
        Returns:
            class_res (dictionary): containing teh result of each classification
        """

        if not self.models_loaded:
            # Loading ontology and model
            self.cso = CSO(silent = self.silent)
            self.model = MODEL(use_full_model=self.use_full_model, silent = self.silent)
            self.models_loaded = True

        t_paper = Paper(paper, self.modules)
        result = Result(self.explanation)


        # Passing parameters to the two classes (synt and sema) and actioning classifiers

        if self.modules in ('syntactic','both'):
            synt_module = synt(self.cso, t_paper)
            result.set_syntactic(synt_module.classify_syntactic())
            if self.explanation:
                result.dump_temporary_explanation(synt_module.get_explanation())
        if self.modules in ('semantic','both'):
            sema_module = sema(self.model, self.cso, self.fast_classification, t_paper)
            result.set_semantic(sema_module.classify_semantic())
            if self.explanation:
                result.dump_temporary_explanation(sema_module.get_explanation())


        postprocess = post(self.model, self.cso, enhancement=self.enhancement, result=result, delete_outliers=self.delete_outliers)
        result = postprocess.filtering_outliers()

        return result.get_dict()


    def batch_run(self, papers, workers=1):
        """Run the CSO Classifier in *BATCH MODE* and with multiprocessing.

        It takes as input a set of papers, which include abstract, title, and keywords and for each one of them returns a
        list of relevant concepts from CSO. This function requires a dictionary of papers, with each id corresponding to
        the metadata of a paper, and few flags: (i) modules, determines whether to run only the syntactic module,
        or the semantic module, or both; (ii) enhancement, controls whether the classifier should infer super-topics,
        i.e., their first direct super-topics or the whole set of topics up until root.

        Args:
            - papers (dictionary): contains the metadata of the papers, e.g., for each paper, there is title, abstract and
                    keywords {"id1":{"title": "","abstract": "","keywords": ""},"id2":{"title": "","abstract": "","keywords": ""}}.

        Returns:
            class_res (dictionary): containing teh result of each classification
        """

        if not isinstance(workers, int):
            raise TypeError("Number of workers must be integer. Got %s instead." % type(workers).__name__)

        if workers < 1:
            raise ValueError("Number of workers must be equal or greater than 1")


        size_of_corpus = len(papers)
        chunk_size = math.ceil(size_of_corpus / workers)
        papers_list = list(chunks(papers, chunk_size))
        annotate = partial(self._batch_run_single_worker)

        with Pool(workers) as p_w:
            result = p_w.map(annotate, papers_list)

        class_res = {k: v for d in result for k, v in d.items()}

        return class_res


    def _batch_run_single_worker(self, papers):
        """Run the CSO Classifier in *BATCH MODE*.

        It takes as input a set of papers, which include abstract, title, and keywords and for each one of them returns a
        list of relevant concepts from CSO. This function requires a dictionary of papers, with each id corresponding to
        the metadata of a paper, and few flags:
        (i) modules, determines whether to run only the syntactic module, or the semantic module, or both;
        (ii) enhancement, controls whether the classifier should infer super-topics, i.e., their first direct
        super-topics or the whole set of topics up until root.


        Args:
            - papers (dictionary): contains the metadata of the papers, e.g., for each paper, there is title, abstract and
                    keywords {"id1":{"title": "","abstract": "","keywords": ""},"id2":{"title": "","abstract": "","keywords": ""}}.
        Returns:
            class_res (dictionary): containing teh result of each classification
        """

        cso = CSO(silent = self.silent)
        model = MODEL(use_full_model=self.use_full_model, silent = self.silent)
        paper = Paper(modules = self.modules)


        # Passing parameters to the two classes (synt and sema)
        synt_module = synt(cso)
        sema_module = sema(model, cso, self.fast_classification)
        postprocess = post(model, cso, enhancement=self.enhancement, delete_outliers=self.delete_outliers)


        # initializing variable that will contain output
        class_res = dict()

        for paper_id, paper_value in papers.items():
            if not self.silent:
                print("Processing:", paper_id)

            paper.set_paper(paper_value)
            result = Result(self.explanation)

            # Passing paper and actioning the classifier
            if self.modules in ('syntactic','both'):
                synt_module.set_paper(paper)
                result.set_syntactic(synt_module.classify_syntactic())
                if self.explanation:
                    result.dump_temporary_explanation(synt_module.get_explanation())
            if self.modules in ('semantic','both'):
                sema_module.set_paper(paper)
                result.set_semantic(sema_module.classify_semantic())
                if self.explanation:
                    result.dump_temporary_explanation(sema_module.get_explanation())
            postprocess.set_result(result)
            result = postprocess.filtering_outliers()

            class_res[paper_id] = result.get_dict()
        return class_res


    def __check_parameters(self, parameters):

        if "modules" in parameters:
            if parameters["modules"] not in ["syntactic", "semantic", "both"]:
                raise ValueError("Field modules must be 'syntactic', 'semantic' or 'both'")

        if "enhancement" in parameters:
            if parameters["enhancement"] not in ["first", "all", "no"]:
                raise ValueError("Field enhancement must be 'first', 'all' or 'no'")

        if "explanation" in parameters:
            if not isinstance(parameters["explanation"], bool):
                raise TypeError("Field explanation must be set to either True or False. Got %s instead." % type(parameters["explanation"]).__name__)

        if "delete_outliers" in parameters:
            if not isinstance(parameters["delete_outliers"], bool):
                raise TypeError("Field delete_outliers must be set to either True or False. Got %s instead." % type(parameters["delete_outliers"]).__name__)

        if "fast_classification" in parameters:
            if not isinstance(parameters["fast_classification"], bool):
                raise TypeError("Field fast_classification must be set to either True or False. Got %s instead." % type(parameters["fast_classification"]).__name__)

        if "silent" in parameters:
            if not isinstance(parameters["silent"], bool):
                raise TypeError("Field silent must be set to either True or False. Got %s instead." % type(parameters["silent"]).__name__)


    @staticmethod
    def setup():
        """ Setting up the classifier: language model, ontology and word2vec model
        """
        download_language_model()

        cso = CSO(load_ontology = False)
        cso.setup()

        MODEL.setup()
        print("Setup completed.")


    @staticmethod
    def update(force = False):
        """ Update the ontology and the word2vec model
        """
        cso = CSO(load_ontology = False)
        cso.update(force = force)

        MODEL.update()
        print("Update completed.")


    @staticmethod
    def version():
        """ Function that returns the version number of different components: classifier and ontology
        """
        config = Config()
        print_header("CLASSIFIER")
        print("CSO Classifier version {}".format(config.get_classifier_version()))


        # This section identifies the last version of the CSO Classifier on pipy.

        running_version = config.get_classifier_version()

        checker = UpdateChecker()
        result = checker.check('cso-classifier', '2.0') #checking if there are versions of the package above 2.0
        latest_version = result.available_version

        if latest_version > running_version:
            print("A more recent version ({}) of the CSO Classifier is available.".format(latest_version))
            print("You can update this package by running 'pip install cso-classifier -U' or follow the instructions on https://github.com/angelosalatino/cso-classifier")
        elif latest_version == config.get_classifier_version():
            print("The version of the CSO Classifier you are using is already up to date.")
        elif latest_version < config.get_classifier_version():
            print("The latest available package is version {} and you are using version {}. There is an error in your configuration file.".format(latest_version,config.get_classifier_version()))

        cso = CSO(load_ontology = False)
        cso.version()
