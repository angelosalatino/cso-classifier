import spacy
from nltk import RegexpParser, tree
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
import re
import itertools


GRAMMAR = "DBW_CONCEPT: {<JJ.*>*<HYPH>*<JJ.*>*<HYPH>*<NN.*>*<HYPH>*<NN.*>+}" #good for syntactic
#GRAMMAR = "DBW_CONCEPT: {<JJ.*>*<NN.*>+}" #good for semantic (or at least for what we know)

class Paper:
    """ A simple abstraction layer for working on the paper object"""

    def __init__(self, paper = None, modules = None):
        """ Initialising the ontology class
        """
        self.title = None
        self.abstract = None
        self.keywords = None
        self._text = None
        self.chunks = None
        self.text_attr = ('title', 'abstract', 'keywords')
        self.tagger = spacy.load('en_core_web_sm', disable=['ner'])

        if modules is not None:
            self.modules = modules

        if paper is not None:
            self.set_paper(paper)



    def set_paper(self, paper):
        """Function that initializes the paper variable in the class.

        Args:
            paper (either string or dictionary): The paper to analyse. It can be
            a full string in which the content
            is already merged or a dictionary  {"title": "","abstract": "","keywords": ""}.

        """
        self.title = None
        self.abstract = None
        self.keywords = None
        self._text = None
        self.semantic_chunks = None
        self.syntactic_chunks = None

        try:
            if isinstance(paper, dict):
                for attr in self.text_attr:
                    try:
                        setattr(self, attr, paper[attr])
                    except KeyError:
                        continue

                self.__treat_keywords()
                self.__text()

            elif isinstance(paper, str):
                self._text = paper.strip()

            else:
                raise TypeError("Error: Unrecognised paper format")

            self.__pre_process()

        except TypeError:
            pass


    def get_text(self):
        """Returns the text of the paper
        """
        return self._text


    def get_semantic_chunks(self):
        """Returns the chunks extracted from the paper (used by the semantic module)
        """
        return self.semantic_chunks


    def get_syntactic_chunks(self):
        """Returns the chunks extracted from the paper (used by the syntactic module)
        """
        return self.syntactic_chunks


    def set_modules(self, modules):
        """Setter for the modules variable"""
        self.modules = modules


    def __text(self):
        """ Text aggregator
        """
        attr_text = [getattr(self, attr) for attr in self.text_attr]
        self._text = '. '.join((s.rstrip('.') for s in attr_text if s is not None))


    def __treat_keywords(self):
        """ Function that handles different version of keyword field
        """
        if self.keywords is None:
            return
        if isinstance(self.keywords, list):
            self.keywords = ', '.join(self.keywords)


    def __part_of_speech_tagger(self, doc):
        """ Part of speech tagger
        Returns:
            text (string): single token
            tag_ (string): POS tag
        """
        for token in doc:
            if token.tag_:
                yield token.text, token.tag_

    def __remove_root_verb(self, doc):
        """ Creates a string in which it removes verbs that are also root of the tree
        """
        new_document = doc.text
        items_to_remove = [(token.text,token.dep_,token.pos_,token.idx, token.idx+len(token.text)) for token in doc if (token.pos_ == "VERB" and token.dep_ == "ROOT")]
        for item in reversed(items_to_remove):
            new_document = new_document[:item[3]] + "." + new_document[item[4]:]
        return new_document


    def __extraxt_semantic_chuncks(self, pos_tags):
        """ Extract chunks of text from the paper taking advantage of the parts of speech previously extracted.
        It uses a grammar
        Returns:
            chunks (list): list of all chunks of text
        """
        grammar_parser = RegexpParser(GRAMMAR)
        chunks = list()
        pos_tags_with_grammar = grammar_parser.parse(pos_tags)
        #print(pos_tags_with_grammar)
        for node in pos_tags_with_grammar:
            if isinstance(node, tree.Tree) and node.label() == 'DBW_CONCEPT': # if matches our grammar
                chunk = ''
                for leaf in node.leaves():
                    concept_chunk = leaf[0]
                    concept_chunk = re.sub('[\=\,\…\’\'\+\-\–\“\”\"\/\‘\[\]\®\™\%]', ' ', concept_chunk)
                    concept_chunk = re.sub('\.$|^\.', '', concept_chunk)
                    concept_chunk = concept_chunk.lower().strip()
                    chunk += ' ' + concept_chunk
                chunk = re.sub('\.+', '.', chunk)
                chunk = re.sub('\s+', ' ', chunk)
                chunks.append(chunk)
        return chunks


    def __extraxt_syntactic_chuncks(self, document):
        """ Extract chunks of text from the paper, using stopwords as delimiter.
        It uses a grammar
        Returns:
            chunks (list): list of all chunks of text
        """
        tokenizer = RegexpTokenizer(r'[\w\-\(\)]*')
        tokens = tokenizer.tokenize(document)
        filtered_words = [a for a in [w if w not in stopwords.words('english') else ':delimiter:' for w in tokens] if a != '']
        matrix_of_tokens = [list(g) for k,g in itertools.groupby(filtered_words,lambda x: x == ':delimiter:') if not k]
        return [" ".join(row).lower() for row in matrix_of_tokens]


    def __pre_process(self):
        """ Pre-processes the paper: identifies the parts of speech and then extracts chunks using a grammar
        """
        ##################### Tagger with spaCy.io
        doc = self.tagger(self._text)

        # =============================================================================
        #         SYNTACTIC
        # =============================================================================
        if self.modules == 'syntactic' or self.modules == 'both':
            ##################### Getting new filtered document removing ROOT NODES(that are VERBS)
            new_filtered_document = self.__remove_root_verb(doc)
            ##################### Extraxting chunks of text base on stop-words
            self.syntactic_chunks = self.__extraxt_syntactic_chuncks(new_filtered_document)
        # =============================================================================
        #         SEMANTIC
        # =============================================================================
        if self.modules == 'semantic' or self.modules == 'both':
            ##################### Getting text and POS in the right configuration
            pos_tags = self.__part_of_speech_tagger(doc)
            ##################### Applying grammar
            self.semantic_chunks = self.__extraxt_semantic_chuncks(list(pos_tags))
