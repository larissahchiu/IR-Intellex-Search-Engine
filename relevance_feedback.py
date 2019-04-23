import re
import nltk
import sys
import getopt
import string
import os
import math
import pandas as pd
from index import *
from ngram_index import process_document
from search_final_q_expansion import *

dataset_file = "../dataset/dataset.csv"

#TODO: decide the constant values (found these ones after some research)
alpha = 1
beta = 0.5
gamma = 0.25

def topK(results, k):
    return results[:k]

#inputs = results, query, dictionary, postings, lengths (this is to get the whole document list)
def rocchio(results, query, postings, length):
    #TODO: implement rocchio formula
    #find top K results then compare with rest of document set
    topKresults = topK(results, 10)


    df = pd.read_csv(dataset_file)
    rocchiovector = {}
    relevantdocweights = {}
    nonrelevantdocweights = {}

    #TODO: calculate the tf for relevant and non relevant docs
    for doc in topKresults:

        content = df[df['document_id'].str.match(doc)].content
        all_words = process_document(content)
        for word in all_words:
            p = obtainPostings(word, postings, offsets)
            if word not in relevantdocweights:
                relevantdocweights[word] = 0.0
            relevantdocweights += p[doc][1]

    for doc in length.keys():
        if doc not in topKresults:
            content = df[df['document_id'].str.match(doc)].content
            all_words = process_document(content)
        for word in all_words:
            p = obtainPostings(word, postings, offsets)
            if word not in nonrelevantdocweights:
                nonrelevantdocweights[word] = 0.0
            nonrelevantdocweights += p[doc][1]



    #TODO: compute new query vector

    #alpha * original query + beta/Dr * relevant docs - gamma/Dnr * non relevant docs

    weights = {}
    for term in offsets.keys():
        p = obtainPostings(term, postings, offsets)
        idf = math.log10(len(length)/len(p))
        for doc in p:
           if term not in weights:
               weights[term] = 0
           if doc in topKresults:
                weights[term] += beta / len(relevantdocweights) * relevantdocweights[term] * idf
           else:
               weights[term] -= gamma / len(nonrelevantdocweights) * nonrelevantdocweights[term] * idf

        if term not in rocchiovector:
            rocchiovector[term] = 0

        if term in query:
            rocchiovector[term] = alpha * rocchiovector[term] + weights[term]
        elif weights[term] > 0:
            rocchiovector[term] = weights[term]

    return rocchiovector











