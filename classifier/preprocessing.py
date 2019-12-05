import spacy
from nltk import RegexpParser, tree
import re

tagger = spacy.load('en_core_web_sm', disable=['parser', 'ner'])

GRAMMAR = "DBW_CONCEPT: {<JJ.*>*<NN.*>+}"

def part_of_speech_tagger(paper):
    doc = tagger(paper)
    for token in doc:
        if token.tag_:
            yield token.text, token.tag_
            

def extraxt_chuncks(pos_tags):        

    grammar_parser = RegexpParser(GRAMMAR)
    
    pos_tags_with_grammar = grammar_parser.parse(pos_tags)
    #print(pos_tags_with_grammar)
    for node in pos_tags_with_grammar:
        if isinstance(node, tree.Tree) and node.label() == 'DBW_CONCEPT': # if matches our grammar 
            concept = ''
            for leaf in node.leaves():
                concept_chunk = leaf[0]
                concept_chunk = re.sub('[\=\,\…\’\'\+\-\–\“\”\"\/\‘\[\]\®\™\%]', ' ', concept_chunk)
                concept_chunk = re.sub('\.$|^\.', '', concept_chunk)
                concept_chunk = concept_chunk.lower().strip()
                concept += ' ' + concept_chunk
            concept = re.sub('\.+', '.', concept)
            concept = re.sub('\s+', ' ', concept)
            yield concept
