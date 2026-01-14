from typing import Any, Dict, List, Set
import json

from .config import Config

class Result:
    """ A simple abstraction layer for retrieving the results """

    def __init__(self, explanation: bool = False, get_weights: bool = False, filter_output: bool = False):
        """ Initialising the Result class.

        Args:
            explanation (bool, optional): If True, enables explanation generation. Defaults to False.
            get_weights (bool, optional): If True, enables weight retrieval. Defaults to False.
            filter_output (bool, optional): If True, enables output filtering. Defaults to False.
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


    def get_dict(self) -> Dict[str, Any]:
        """ Returns a dictionary containing all relevant objects

        Returns:
            Dict[str, Any]: Dictionary representation of the result.
        """
        return {attr: getattr(self, attr) for attr in self.result_attr}


    def set_syntactic(self, syntactic: List[str]) -> None:
        """ Sets the syntactic variable

        Args:
            syntactic (List[str]): List of syntactic topics.
        """
        self.syntactic = syntactic
        self.__merge()


    def get_syntactic(self) -> List[str]:
        """ Gets the syntactic variable

        Returns:
            List[str]: List of syntactic topics.
        """
        return self.syntactic


    def set_semantic(self, semantic: List[str]) -> None:
        """ Sets the semantic variable

        Args:
            semantic (List[str]): List of semantic topics.
        """
        self.semantic = semantic
        self.__merge()


    def get_semantic(self) -> List[str]:
        """ Gets the semantic variable

        Returns:
            List[str]: List of semantic topics.
        """
        return self.semantic


    def set_union(self, union: List[str]) -> None:
        """ Sets the union variable

        Args:
            union (List[str]): List of union topics.
        """
        self.union = union


    def get_union(self) -> List[str]:
        """ Gets the union variable

        Returns:
            List[str]: List of union topics.
        """
        return self.union


    def set_enhanced(self, enhanced: Dict[str, Any]) -> None:
        """ Sets the enhanced variable

        Args:
            enhanced (Dict[str, Any]): Dictionary of enhanced topics.
        """
        self.enhanced = [x for x in list(enhanced.keys()) if x not in self.union]
        self.__complete_explanation(enhanced)


    def get_enhanced(self) -> List[str]:
        """ Gets the enhanced variable

        Returns:
            List[str]: List of enhanced topics.
        """
        return self.enhanced


    def __merge(self) -> None:
        """ Function that fills the union object
        """
        self.union = list(set(self.syntactic + self.semantic))
        
        
    def set_syntactic_topics_weights(self, syntactic_weights: Dict[str, float]) -> None:
        """ Sets the syntactic_weights variable

        Args:
            syntactic_weights (Dict[str, float]): Dictionary of syntactic topic weights.
        """
        self.syntactic_weights = syntactic_weights


    def get_syntactic_topics_weights(self) -> Dict[str, float]:
        """ Gets the syntactic_weights variable

        Returns:
            Dict[str, float]: Dictionary of syntactic topic weights.
        """
        return self.syntactic_weights


    def set_semantic_topics_weights(self, semantic_weights: Dict[str, float]) -> None:
        """ Sets the semantic_weights variable

        Args:
            semantic_weights (Dict[str, float]): Dictionary of semantic topic weights.
        """
        self.semantic_weights = semantic_weights


    def get_semantic_topics_weights(self) -> Dict[str, float]:
        """ Gets the semantic_weights variable

        Returns:
            Dict[str, float]: Dictionary of semantic topic weights.
        """
        return self.semantic_weights
    
    
    def set_filtered_syntactic(self, filtered_syntactic: List[str]) -> None:
        """ Set the filtered syntactic topics

        Args:
            filtered_syntactic (List[str]): List of filtered syntactic topics.
        """
        self.filtered_syntactic = filtered_syntactic
        
        
    def get_filtered_syntactic(self) -> List[str]:
        """ Get the filtered syntactic topics

        Returns:
            List[str]: List of filtered syntactic topics.
        """
        return self.filtered_syntactic
     
    def set_filtered_semantic(self, filtered_semantic: List[str]) -> None:
        """ Set the filtered semantic topics

        Args:
            filtered_semantic (List[str]): List of filtered semantic topics.
        """
        self.filtered_semantic = filtered_semantic
        
        
    def get_filtered_semantic(self) -> List[str]:
        """ Get the filtered semantic topics

        Returns:
            List[str]: List of filtered semantic topics.
        """
        return self.filtered_semantic
     
     
    def set_filtered_union(self, filtered_union: List[str]) -> None:
        """ Set the filtered union topics

        Args:
            filtered_union (List[str]): List of filtered union topics.
        """
        self.filtered_union = filtered_union
        
        
    def get_filtered_union(self) -> List[str]:
        """ Get the filtered union topics

        Returns:
            List[str]: List of filtered union topics.
        """
        return self.filtered_union
     
    def set_filtered_enhanced(self, filtered_enhanced: List[str]) -> None:
        """ Set the filtered enhanced topics

        Args:
            filtered_enhanced (List[str]): List of filtered enhanced topics.
        """
        self.filtered_enhanced = filtered_enhanced
        
        
    def get_filtered_enhanced(self) -> List[str]:
        """ Get the filtered enhanced topics

        Returns:
            List[str]: List of filtered enhanced topics.
        """
        return self.filtered_enhanced
        

    def dump_temporary_explanation(self, temporary_explanation: Dict[str, Set[str]]) -> None:
        """ It dumps the temporary explanation. After it will be reorganised
        better for all topics (including the enhanced ones)

        Args:
            temporary_explanation (Dict[str, Set[str]]): Temporary explanation dictionary.
        """
        if self.explanation_flag:
            for topic, chunks in temporary_explanation.items():
                if topic not in self.explanation:
                    self.explanation[topic] = set()
                self.explanation[topic] = self.explanation[topic].union(chunks)


    def __complete_explanation(self, enhanced: Dict[str, Any]) -> None:
        """ It creates the explanation also for the enhanced topics

        Args:
            enhanced (Dict[str, Any]): Dictionary of enhanced topics with lineage.
        """

        if self.explanation_flag:
            for enhanced_topic, value in enhanced.items():
                if enhanced_topic not in self.explanation:
                    self.explanation[enhanced_topic] = set()
                self.explanation[enhanced_topic] = self.explanation[enhanced_topic].union(*[self.explanation[topic] for topic in value['broader of'] if topic in self.explanation])
            
            all_topics = set(self.enhanced+self.union)
            self.explanation = {topic: list(value) for topic, value in self.explanation.items() if topic in all_topics}

    
    def get_croissant_specification(self, filename: Optional[str] = None, print_output: bool = False) -> None:
        """Generates a Croissant JSON-LD specification for the classification results.

        This method creates a Croissant specification based on the attributes of the
        Result object, which reflects the classifier's output configuration (e.g.,
        whether explanations or weights are included). The specification can be saved
        to a file and optionally printed to the console.

        Args:
            filename (Optional[str], optional): The name of the file to save the Croissant specification.
                                                If None or an empty string, the specification is not saved to a file.
                                                Defaults to None.
            print_output (bool, optional): If True, prints the Croissant specification to stdout.
                                           Defaults to False.

        Raises:
            RuntimeError: If the Croissant base specification file cannot be loaded.
            ValueError: If `filename` is provided but is an empty string.
        """
        config = Config()
        
        try:
            # Load the base Croissant specification
            with open(config.get_croissant_base_specification_path(), 'r') as croissant_base_file:
                croissant_base = json.load(croissant_base_file)
            
            fields = list()
            for attribute in croissant_base["recordSet"][0]["field"]:
                if attribute["name"] in self.result_attr:
                    fields.append(attribute)
            croissant_base["recordSet"][0]["field"] = fields

            # Handle saving to file and printing output
            if filename is not None and filename != "":
                with open(filename, 'w') as output_file:
                    json.dump(croissant_base, output_file, indent=4)
                
                if print_output:
                    print(json.dumps(croissant_base, indent=4))
            else:
                raise ValueError(f"ERROR: Please provide a correct filename. Currently provided '{filename}'.")
         
        except Exception:
            raise RuntimeError(
                f"Failed to load the Croissant base file from '{config.get_croissant_base_specification_path()}'.\n"
                f"You can find a copy of this file on {config.get_croissant_base_specification_remote_path()}"
            )