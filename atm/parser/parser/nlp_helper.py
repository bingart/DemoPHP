# coding=utf-8

import re
import string
from gensim.summarization import summarize
from gensim.summarization import keywords

class NLPHelper:
    
    def __init__(self):
        print("created")
    
    @staticmethod
    def getSummary(source, ratio = 0.15, wordCount = 64):
        try:
            if len(source.split()) <= wordCount:
                return source
            else:
                return summarize(source, ratio, wordCount)
        except Exception as err :
            print(err)
            return None

    @staticmethod
    def getKeywords(source, ratio = 0.2):
        if source != None and len(source) > 0:
            return keywords(source, ratio)
        else:
            return None
        
if __name__=="__main__":
    print("main")
    text = "Thomas A. Anderson is a man living two lives. By day he is an " + \
        "average computer programmer and by night a hacker known as " + \
        "Neo. Neo has always questioned his reality, but the truth is " + \
        "far beyond his imagination. Neo finds himself targeted by the " + \
        "police when he is contacted by Morpheus, a legendary computer " + \
        "hacker branded a terrorist by the government. Morpheus awakens " + \
        "Neo to the real world, a ravaged wasteland where most of " + \
        "humanity have been captured by a race of machines that live " + \
        "off of the humans' body heat and electrochemical energy and " + \
        "who imprison their minds within an artificial reality known as " + \
        "the Matrix. As a rebel against the machines, Neo must return to " + \
        "the Matrix and confront the agents: super-powerful computer " + \
        "programs devoted to snuffing out Neo and the entire human " + \
        "rebellion. "
    summary = NLPHelper.getSummary(text)
    keys = NLPHelper.getKeywords(summary)
    keys2 = NLPHelper.getKeywords(text)
    print (summary)
    print (keys)
    print (keys2)
    print("exit")
    
    