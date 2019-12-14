class Result:
    """ A simple abstraction layer for retrieving the results """
    
    def __init__(self, explanation = False):
        """ Initialising the ontology class
        """
        self.syntactic = list()
        self.semantic = list()
        self.union = list()
        self.enhanced = list()
        self.explanation_flag = explanation
        if self.explanation_flag:
            self.explanation = dict()
            self.result_attr = ('syntactic', 'semantic', 'union', 'enhanced', 'explanation')
        else:
            self.result_attr = ('syntactic', 'semantic', 'union', 'enhanced')


    def merge(self):
        """ Function that fills the union object
        """
        self.union = list(set(self.syntactic + self.semantic))
        
    
    def get_dict(self):
        """ Returns a dictionary containing all relevant objects
        """
        return {attr: getattr(self, attr) for attr in self.result_attr}
    
    
    def set_syntactic(self, syntactic):
        """ Sets the syntactic variable
        """
        self.syntactic = syntactic
        self.merge()
        
        
    def set_semantic(self, semantic):
        """ Sets the semantic variable
        """
        self.semantic = semantic
        self.merge()
        
        
    def set_enhanced(self, enhanced):
        """ Sets the enhanced variable
        """
        self.enhanced = [x for x in list(enhanced.keys()) if x not in self.union]
        self.complete_explanation(enhanced)
        
    
    def dump_temporary_explanation(self, temporary_explanation):
        """ It dumps the temporary explanation. After it will be reorganised better for all topics (including the enhanced ones)
        """
        if self.explanation_flag:
            for topic, chunks in temporary_explanation.items():
                if topic not in self.explanation:
                    self.explanation[topic] = set()
                self.explanation[topic] = self.explanation[topic].union(chunks)
            
                    
    def complete_explanation(self, enhanced):
        """ It creates the explanation also for the enhanced topics
        """
        
        if self.explanation_flag:
            for enhanced_topic, value in enhanced.items():
                if enhanced_topic not in self.explanation:
                    self.explanation[enhanced_topic] = set()
                self.explanation[enhanced_topic] = self.explanation[enhanced_topic].union(*[self.explanation[topic] for topic in value['broader of'] if topic in self.explanation])
        
            self.explanation = {topic: list(value) for topic, value in self.explanation.items()}
                
                