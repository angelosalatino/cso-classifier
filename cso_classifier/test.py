import json

from .classifier import CSOClassifier

def test_classifier_single_paper():
    """ Functionality that tests the classifier with a single paper.
    It loads two papers, it calls the classifier with certain parameters and then
    it prints the results over the console.
    """

    paper = {
        "title": "De-anonymizing Social Networks",
        "abstract": "Operators of online social networks are increasingly sharing potentially "
        "sensitive information about users and their relationships with advertisers, application "
        "developers, and data-mining researchers. Privacy is typically protected by anonymization, "
        "i.e., removing names, addresses, etc. We present a framework for analyzing privacy and "
        "anonymity in social networks and develop a new re-identification algorithm targeting "
        "anonymized social-network graphs. To demonstrate its effectiveness on real-world networks, "
        "we show that a third of the users who can be verified to have accounts on both Twitter, a "
        "popular microblogging service, and Flickr, an online photo-sharing site, can be re-identified "
        "in the anonymous Twitter graph with only a 12% error rate. Our de-anonymization algorithm is "
        "based purely on the network topology, does not require creation of a large number of dummy "
        "\"sybil\" nodes, is robust to noise and all existing defenses, and works even when the overlap "
        "between the target network and the adversary's auxiliary information is small.",
        "keywords": "data mining, data privacy, graph theory, social networking (online)"
        }



    print(paper["title"])
    print(paper["abstract"])
    print(paper["keywords"])

    cso_classifier = CSOClassifier(explanation = True)
    result = cso_classifier.run(paper)

    print(json.dumps(result))


def test_classifier_batch_mode():
    """ Functionality that tests the classifier in batch mode.
    It loads two papers, it calls the classifier with certain parameters and then it prints the results over the console.
    """

    papers = dict()
    papers['paper1'] = {
        "title": "De-anonymizing Social Networks",
        "abstract": "Operators of online social networks are increasingly sharing potentially sensitive information about users and their relationships with advertisers, application developers, and data-mining researchers. Privacy is typically protected by anonymization, i.e., removing names, addresses, etc. We present a framework for analyzing privacy and anonymity in social networks and develop a new re-identification algorithm targeting anonymized social-network graphs. To demonstrate its effectiveness on real-world networks, we show that a third of the users who can be verified to have accounts on both Twitter, a popular microblogging service, and Flickr, an online photo-sharing site, can be re-identified in the anonymous Twitter graph with only a 12% error rate. Our de-anonymization algorithm is based purely on the network topology, does not require creation of a large number of dummy \"sybil\" nodes, is robust to noise and all existing defenses, and works even when the overlap between the target network and the adversary's auxiliary information is small.",
        "keywords": "data mining, data privacy, graph theory, social networking (online)"
        }
    papers['paper2'] = {
        "title": "Automatic Classification of Springer Nature Proceedings with Smart Topic Miner",
        "abstract": "The process of classifying scholarly outputs is crucial to ensure timely access to knowledge. However, this process is typically carried out manually by expert editors, leading to high costs and slow throughput. In this paper we present Smart Topic Miner (STM), a novel solution which uses semantic web technologies to classify scholarly publications on the basis of a very large automatically generated ontology of research areas. STM was developed to support the Springer Nature Computer Science editorial team in classifying proceedings in the LNCS family. It analyses in real time a set of publications provided by an editor and produces a structured set of topics and a number of Springer Nature Classification tags, which best characterise the given input. In this paper we present the architecture of the system and report on an evaluation study conducted with a team of Springer Nature editors. The results of the evaluation, which showed that STM classifies publications with a high degree of accuracy, are very encouraging and as a result we are currently discussing the required next steps to ensure large-scale deployment within the company.",
        "keywords": "Scholarly data, Ontology learning, Bibliographic data, Scholarly ontologies, Data mining, Conference proceedings Metadata"
        }


    for key, paper in papers.items():
        print(key)
        print(paper["title"])
        print(paper["abstract"])
        print(paper["keywords"])

    cso_classifier = CSOClassifier()
    results = cso_classifier.batch_run(papers, workers = 2)

    print(results)
