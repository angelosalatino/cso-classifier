#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 15 22:59:48 2018

@author: angelosalatino
"""


import miscClassify as m
import json



def re_classify():
    
    with open('data/info.json', 'r') as handle:
        p = json.load(handle)
    
#    new_clas = m.classify_papers_batch1(p)
    new_clas = m.classify_papers_batchHybrid(p)

    with open('data/new_classification_complete_topics9Jan7.json', 'w') as outfile:
        json.dump(new_clas, outfile, indent=4)


def classifySingle(paper):
    
    with open('data/info.json', 'r') as handle:
        papers = json.load(handle)
    
    clas = m.classify_paper(papers, paper)
    
    print(json.dumps(clas, indent=4, sort_keys=True))

def main():

    re_classify()


if __name__ == '__main__':
    """ Main entry point to the script """
    main()
    