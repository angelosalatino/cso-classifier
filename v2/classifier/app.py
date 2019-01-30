#!/data/web/rexplore2.kmi.open.ac.uk/www/API/cso-c-eval/venv/bin python
# -*- coding: utf-8 -*-
"""
Computer Science Ontology based text classifier (July 2018)
"""
from flask import Flask, abort, request, jsonify, Response
from flask_restful import Api
from flask_cors import CORS
import json
import hashlib

## external functions
import misc
from functions.stringmatcher import CSOClassifier as sm
from functions.word_embeddings import CSOSemanticClassifier as we
import multiprocessing as mp


# Create an instance of the Flask object
app = Flask(__name__)
# Allow cross-origin resource sharing
CORS(app, resources={r"/v0.1/*": {"origins": "*"}})
# Create Application Programming Interface object by passing the app object
api = Api(app, prefix='/v0.1')

@app.route('/', methods=['GET'])
def hello():
    return 'The API is up and running.'


@app.route('/classify', methods=['POST'])
def classify():
    # Validate content type
    if request.content_type != 'application/json':
        abort(400)  # Bad Request!

    # Parse data into dictionary
    data = request.data
    data_dictionary = json.loads(data)
    paper = data_dictionary["paper"]
    doi = data_dictionary["doi"]

    try:
#        # Create an instance of the CSO_classifier class
#        clf = CSOClassifier(version=int(data_dictionary["ontology_version"]))
#
#        # Load CSO data from local file
#        clf.load_cso()
#        # Classify the topics within the paper
#        result = clf.classify(paper,
#                              num_narrower=int(data_dictionary["num_narrower"]),
#                              min_similarity=float(data_dictionary["min_similarity"]),
#                              climb_ont=data_dictionary["climb_ont"],
#                              verbose=True)
#        response = dict()
#        response["verbose"] = result
#        response["list"] = clf.strip_explanation(result)
    
        # Loads CSO data from local file
        cso, model = misc.load_ontology_and_model()
        
        # Passing parematers to the two classes (synt and sem)
        clf = sm(cso, paper)
        clf2 = we(model, cso, paper)
        
        # Creating shared structure
        manager = mp.Manager()
        result = manager.dict()
        
        # Initialising processes
        processes1 = clf.run(result)
        processes2 = clf2.run(result)
        processes = processes1 + processes2
        
        # Running Processes
        [x.start() for x in processes]
        [x.join() for x in processes]
        
        # Joining the structures
        result["unique"] = list(set(
                            result["stringmatcher"]["extracted"] + result["stringmatcher"]["inferred"] + 
                            result["stringsimilarity"]["extracted"] + result["stringsimilarity"]["inferred"] +
                            result["syntsema"]["extracted"] + result["syntsema"]["inferred"] +
                            result["advsyntsema"]["extracted"] + result["advsyntsema"]["inferred"]
                            ))
        
        
        ## LOG analysed paper
        z = {**paper, **result}
        z["doi"] = doi
        
        filename = hashlib.md5(doi.encode()).hexdigest()
        with open('papers/'+filename, 'w') as outfile:
            json.dump(z, outfile)
        
        
        
        #print(json.dumps(result.copy(), indent=2, sort_keys=False))
        
        return jsonify(result.copy()), 200, {'Content-Type': 'application/json; charset=utf-8'}
    
    except ValueError:
        abort(400)  # Bad Request!


if __name__ == '__main__':
    print('running as main')
    app.run(host='0.0.0.0', debug=False, port='2004')