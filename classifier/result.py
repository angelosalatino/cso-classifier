class Result:
    """ A simple abstraction layer for retrieving the results """
    
    def __init__(self, paper = None):
        """ Initialising the ontology class
        """
        self.syntactic = list()
        self.semantic = list()
        self.union = list()
        self.enhanced = list()
        self.result_attr = ('syntactic', 'semantic', 'union', 'enhanced')

    def merge(self):
        self.union = list(set(self.syntactic + self.semantic))
        
    
    def get_dict(self):
        return {attr: getattr(self, attr) for attr in self.result_attr}
    
    def set_syntactic(self, syntactic):
        self.syntactic = syntactic
        self.merge()
        
    def set_semantic(self, semantic):
        self.semantic = semantic
        self.merge()
        
    def set_enhanced(self, enhanced):
        self.enhanced = [x for x in list(enhanced.keys()) if x not in self.union]