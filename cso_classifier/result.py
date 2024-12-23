class Result:
    """ A simple abstraction layer for retrieving the results """

    def __init__(self, explanation = False, get_weights=False, filter_output=False):
        """ Initialising the ontology class
        """
        self.syntactic = list()
        self.semantic = list()
        self.union = list()
        self.enhanced = list()
        self.result_attr = ('syntactic', 'semantic', 'union', 'enhanced')
        
        self.explanation_flag = explanation
        if self.explanation_flag:
            self.explanation = dict()
            self.result_attr += ('explanation',)

        self.get_weights = get_weights
        if self.get_weights:
            self.syntactic_weights = dict()
            self.semantic_weights = dict()
            self.result_attr += ('syntactic_weights','semantic_weights',)
        
        self.filter_output = False
        if filter_output:
            self.filter_output = True
            self.filtered_syntactic = list()
            self.filtered_semantic = list()
            self.filtered_union = list()
            self.filtered_enhanced = list()
            self.result_attr += ('filtered_syntactic', 'filtered_semantic', 'filtered_union', 'filtered_enhanced',)


    def get_dict(self):
        """ Returns a dictionary containing all relevant objects
        """
        return {attr: getattr(self, attr) for attr in self.result_attr}


    def set_syntactic(self, syntactic):
        """ Sets the syntactic variable
        """
        self.syntactic = syntactic
        self.__merge()


    def get_syntactic(self):
        """ Gets the syntactic variable
        """
        return self.syntactic


    def set_semantic(self, semantic):
        """ Sets the semantic variable
        """
        self.semantic = semantic
        self.__merge()


    def get_semantic(self):
        """ Gets the semantic variable
        """
        return self.semantic


    def set_union(self, union):
        """ Sets the union variable
        """
        self.union = union


    def get_union(self):
        """ Gets the syntactic variable
        """
        return self.union


    def set_enhanced(self, enhanced):
        """ Sets the enhanced variable
        """
        self.enhanced = [x for x in list(enhanced.keys()) if x not in self.union]
        self.__complete_explanation(enhanced)


    def get_enhanced(self):
        """ Gets the enhanced variable
        """
        return self.enhanced


    def __merge(self):
        """ Function that fills the union object
        """
        self.union = list(set(self.syntactic + self.semantic))
        
        
    def set_syntactic_topics_weights(self, syntactic_weights):
        """ Sets the syntactic_weights variable
        """
        self.syntactic_weights = syntactic_weights


    def get_syntactic_topics_weights(self):
        """ Gets the syntactic_weights variable
        """
        return self.syntactic_weights


    def set_semantic_topics_weights(self, semantic_weights):
        """ Sets the semantic_weights variable
        """
        self.semantic_weights = semantic_weights


    def get_semantic_topics_weights(self):
        """ Gets the semantic_weights variable
        """
        return self.semantic_weights
    
    
    def set_filtered_syntactic(self, filtered_syntactic):
        """ Set the filtered syntactic topics
        """
        self.filtered_syntactic = filtered_syntactic
        
        
    def get_filtered_syntactic(self):
         """ Get the filtered syntactic topics
         """
         return self.filtered_syntactic
     
    def set_filtered_semantic(self, filtered_semantic):
        """ Set the filtered semantic topics
        """
        self.filtered_semantic = filtered_semantic
        
        
    def get_filtered_semantic(self):
         """ Get the filtered semantic topics
         """
         return self.filtered_semantic
     
     
    def set_filtered_union(self, filtered_union):
        """ Set the filtered union topics
        """
        self.filtered_union = filtered_union
        
        
    def get_filtered_union(self):
         """ Get the filtered union topics
         """
         return self.filtered_union
     
    def set_filtered_enhanced(self, filtered_enhanced):
        """ Set the filtered enhanced topics
        """
        self.filtered_enhanced = filtered_enhanced
        
        
    def get_filtered_enhanced(self):
         """ Get the filtered enhanced topics
         """
         return self.filtered_enhanced
        

    def dump_temporary_explanation(self, temporary_explanation):
        """ It dumps the temporary explanation. After it will be reorganised
        better for all topics (including the enhanced ones)
        """
        if self.explanation_flag:
            for topic, chunks in temporary_explanation.items():
                if topic not in self.explanation:
                    self.explanation[topic] = set()
                self.explanation[topic] = self.explanation[topic].union(chunks)


    def __complete_explanation(self, enhanced):
        """ It creates the explanation also for the enhanced topics
        """

        if self.explanation_flag:
            for enhanced_topic, value in enhanced.items():
                if enhanced_topic not in self.explanation:
                    self.explanation[enhanced_topic] = set()
                self.explanation[enhanced_topic] = self.explanation[enhanced_topic].union(*[self.explanation[topic] for topic in value['broader of'] if topic in self.explanation])
            
            all_topics = set(self.enhanced+self.union)
            self.explanation = {topic: list(value) for topic, value in self.explanation.items() if topic in all_topics}
