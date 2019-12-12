import spacy
from nltk import RegexpParser, tree
import re

tagger = spacy.load('en_core_web_sm', disable=['parser', 'ner'])
GRAMMAR = "DBW_CONCEPT: {<JJ.*>*<HYPH>*<JJ.*>*<HYPH>*<NN.*>*<HYPH>*<NN.*>+}" #good for syntactic
#GRAMMAR = "DBW_CONCEPT: {<JJ.*>*<NN.*>+}" #good for semantic (or at least for what we know)

class Paper:
    """ A simple abstraction layer for working on the paper object"""
    
    def __init__(self, paper = None):
        """ Initialising the ontology class
        """
        self.title = None
        self.abstract = None
        self.keywords = None
        self._text = None
        self.chunks = None
        self.text_attr = ('title', 'abstract', 'keywords')
        
        if paper is not None:
            self.set_paper(paper)
        
    
    
    def set_paper(self, paper):
        """Function that initializes the paper variable in the class.

        Args:
            paper (either string or dictionary): The paper to analyse. It can be a full string in which the content
            is already merged or a dictionary  {"title": "","abstract": "","keywords": ""}.

        """
        self.title = None
        self.abstract = None
        self.keywords = None
        self._text = None
        self.chunks = None

        try:
            if isinstance(paper, dict):              
                for attr in self.text_attr:
                    try: 
                        setattr(self, attr, paper[attr])
                    except KeyError:
                        continue
                    
                self.treat_keywords()
                self.text()
                
            elif isinstance(paper, str):
                self._text = paper.strip()
            
            else:
                raise TypeError("Error: Unrecognised paper format")
                return
        
            self.pre_process()
            
        except TypeError:
            pass


    def text(self):
        """ Text aggregator
        """
        attr_text = [getattr(self, attr) for attr in self.text_attr]
        self._text = '. '.join((s.rstrip('.') for s in attr_text if s is not None))


    def treat_keywords(self):
        """ Function that handles different version of keyword field
        """
        if self.keywords is None:
            return
        if isinstance(self.keywords, list):
            self.keywords = ', '.join(self.keywords)


    def part_of_speech_tagger(self):
        """ Part of speech tagger
        Returns:
            text (string): single token
            tag_ (string): POS tag
        """
        doc = tagger(self._text)
        for token in doc:
            if token.tag_:
                yield token.text, token.tag_
            

    def extraxt_chuncks(self, pos_tags):
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
                
                
    def pre_process(self):
        """ Pre-processes the paper: identifies the parts of speech and then extracts chunks using a grammar
        """
        ##################### Tokenizer with spaCy.io
        pos_tags = self.part_of_speech_tagger()
        ##################### Applying grammar          
        self.chunks = self.extraxt_chuncks(list(pos_tags))  
     
        
    def get_chunks(self):
        """Returns the chunks extracted from the paper
        """
        return self.chunks