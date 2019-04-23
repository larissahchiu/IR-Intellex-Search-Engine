import re
import nltk
import sys
import getopt
import pickle
import string
import os
from nltk.stem import PorterStemmer
import math
from heap import heap
from query_expansion import *
import gzip

# Total number of legal documents
numDocs = 17137
# Cache previously accessed postings for quicker access
cachedPostings = {}

# Read the document lengths dictionary into doc_lengths
doc_lengths_file = open('lengths.txt', 'rb')
doc_lengths = pickle.load(doc_lengths_file)

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

dictionary_file = postings_file = file_of_queries = output_file_of_results = None
	
try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError as err:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file  = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        file_of_queries = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None :
    usage()
    sys.exit(2)

# Preprocesses the token from the query to remove its punctuation, convert to lowercase, remove digits and stem.
def preprocess_token(token):
    punc_set = set(string.punctuation)
    ps = PorterStemmer()

    #remove punctuation from token
    token = ''.join(ch for ch in token if ch not in punc_set)

    #remove numbers from token:
    if any(char.isdigit() for char in token):
        token = ''.join(ch for ch in token if not ch.isdigit())

    #convert to lowercase and do stemming
    token = ps.stem(token.lower())

    return token

# Reads the dictionary file and returns an offset dictionary which has tokens as keys and byte offsets as values
def readDict(dictionary_file):
    offsets = {}
    dictionary = open(dictionary_file, "r", encoding='utf-8')
    for line in dictionary.readlines():
        line = line.strip().split(' ')
        offsets[line[0]] = line[1]

    return offsets

# Reads the query file line by line, parses and evaluates the query, and writes the result to the output file
def readQueries(file_of_queries, offsets, postings, all_ids):
    queries = open(file_of_queries, "r")
    output = open(file_of_output, "w")

    for line in queries.readlines():
        line = line.strip()
        parsedQuery = ''
        result = []
        if ' AND ' in line:
            parsedQuery = parse_boolean(line)
            result = cosine_score(parsedQuery, postings, offsets, True)
        else:
            parsedQuery = parse_free(line)
            result = cosine_score(parsedQuery, postings, offsets)
        
        output.write(' '.join(map(str, result)) + "\n")

# Returns a postings list if the token is present in the index
def obtainPostings(token, postings, offsets):
    # Use caching to make lookup more efficient as the length of the postings is always first accessed
    # in #obtain_query_weights
    if token in cachedPostings:
        return cachedPostings[token]
    else:
        if token in offsets:
            postings.seek(int(offsets[token]))
            tokenPostings = pickle.load(postings)
            cachedPostings[token] = tokenPostings
            return tokenPostings
        elif len(token.split(' ')) > 1:
            tokens = token.split(' ')
            # Obtain postings of a bigram using the positional postings list
            if len(tokens) == 2:
                first_token_postings = obtainPostings(tokens[0], postings, offsets)
                second_token_postings = obtainPostings(tokens[1], postings, offsets)
                intersect_postings = positional_intersect(first_token_postings, second_token_postings, 1)
                cachedPostings[token] = intersect_postings
                return intersect_postings
            # Obtain postings of a trigram using the positional postings list
            elif len(tokens) == 3:
                first_token_postings = obtainPostings(tokens[0], postings, offsets)
                second_token_postings = obtainPostings(tokens[1], postings, offsets)
                third_token_postings = obtainPostings(tokens[2], postings, offsets)
                intersect_postings_1 = positional_intersect(first_token_postings, second_token_postings, 1)
                intersect_postings_2 = positional_intersect(second_token_postings, third_token_postings, 1)
                final_intersect = merge_postings(intersect_postings_1, intersect_postings_2)
                cachedPostings[token] = final_intersect
                return final_intersect
        else:
            cachedPostings[token] = []
            return []

# Splits queries while retaining the phrases within free-text queries
def split_query(q):
    q = q.split(' ')
    res = []
    stack = []
    for word in q:
        if len(stack) > 0 or any(char == '\"' for char in word):
            if len(stack) > 0 and any(char == '\"' for char in word):
                phrase = word
                while len(stack) > 0:
                    phrase = stack.pop() + ' ' + phrase
                res.append(phrase)
            else:
                stack.append(word)
        else:
            res.append(word)

    return res

# Parses the query into a dictionary of term - raw term frequency pairs
def parse_free(query):
    output = {}
    tokens = split_query(query)

    for token in tokens:
        stemmed = preprocess_token(token)
        if stemmed not in output:
            output[stemmed] = 1
        else:
            output[stemmed] += 1

    return output

# Preprocesses the tokens in a boolean query to ensure that phrases are retained
def preprocess_boolean(token_lst):
    punc_set = set(string.punctuation)
    ps = PorterStemmer()
    preprocessed = []
    for ngram in token_lst:
        ngram_lst = ngram.split(' ')
        pp_token = []
        for ele in ngram_lst:
            if ele == '':
                continue
            ele = ''.join(ch for ch in ele if ch not in punc_set)

            if any(char.isdigit() for char in ele):
                ele = ''.join(ch for ch in ele if not ch.isdigit())
            ele = ps.stem(ele.lower())
            pp_token.append(ele)
        if len(pp_token) > 0:
            preprocessed.append(' '.join(pp_token))
    return preprocessed

# Parses a boolean 'AND' query into a dictionary of term - raw term frequency pairs
def parse_boolean(query):
    output = {}
    token_list = re.split(' AND ', query)

    preprocessed_lst = preprocess_boolean(token_list)

    for ele in preprocessed_lst:
        if ele not in output:
            output[ele] = 1
        else:
            output[ele] += 1
    return output

# Calculates the tf-idf of a query term using logarithm term frequency and inverse document frequency
def tf_idf(term, termFreq, docFreq):
    ans = 1 + math.log10(termFreq)
    idf = math.log10(numDocs/docFreq)
    ans *= idf

    return ans

# Returns an array containing all the relevant documents to the query ranked by cosine scores
def cosine_score(query, postings, offsets, booleanQuery=False):
    scores = {}
    query_weights = obtain_query_weights(query, postings, offsets)
    merged_postings = []

    if booleanQuery == True:
        # Obtain a merged postings list for the boolean query instead of using individual lists
        for term in query_weights:
            term_postings = obtainPostings(term, postings, offsets)
            if len(merged_postings) == 0:
                merged_postings = term_postings
            else:
                merged_postings = merge_postings(merged_postings, term_postings)

    for term, weight in query_weights.items():
        if booleanQuery == True:
            term_postings = merged_postings
        else:
            term_postings = obtainPostings(term, postings, offsets)
        for doc in term_postings:
            doc_id = doc['docID']
            doc_term_weight = doc['freq']
            if doc_id in scores:
                scores[doc_id] += weight * doc_term_weight
            else:
                scores[doc_id] = weight * doc_term_weight
    
    for doc_id, score in scores.items():
        scores[doc_id] = scores[doc_id]/doc_lengths[doc_id]
    
    # Heapify scores to allow for efficient extraction
    h = heap()
    h.build_heap(scores)
    h_size = h.curr_size
    result_lst = []

    for i in range(h_size):
        result_lst.append(h.remove_max()[0])

    return result_lst

# Returns a dictionary containing the tf-idf of each term in a query
def obtain_query_weights(query, postings, offsets):
    vector = {}
    for term, freq in query.items():
        doc_freq = len(obtainPostings(term, postings, offsets))
        if doc_freq != 0:
            query_weight = tf_idf(term, freq, doc_freq)
            vector[term] = query_weight

    # perform cosine normalisation on query's tf-idf
    sum = 0
    for term, freq in vector.items():
        sum += math.pow(freq, 2)
    
    sum = math.pow(sum, 0.5)

    for term, freq in vector.items():
        vector[term] = vector[term]/sum
    
    return vector

# Returns the intersection between 2 postings lists
# Used for obtaining postings for phrasal queries as the dictionary that's being used is a unigram model
def positional_intersect(postings_1, postings_2, k):
    merged = []
    i = 0
    j = 0
    while i < len(postings_1) and j < len(postings_2):
        if postings_1[i]['docID'] == postings_2[j]['docID']:
            results = []
            positions_1 = postings_1[i]['positions']
            positions_2 = postings_2[j]['positions']
            m = 0

            while (m < len(positions_1)):
                h = 0
                while (h < len(positions_2)):
                    distance = abs(positions_1[m] - positions_2[h])
                    if (distance <= k):
                        results.append(h)
                    elif positions_2[h] > positions_1[m]:
                        break
                    h += 1

                for idx in results:
                    distance = abs(positions_2[idx] - positions_1[m])
                    if distance > k:
                        results.remove(idx)
                if (len(results) > 0):
                    obj = {}
                    obj['docID'] = postings_1[i]['docID']
                    obj['freq'] = postings_1[i]['freq']
                    merged.append(obj)
                m += 1

            i += 1
            j += 1
        elif postings_1[i]['docID'] > postings_2[j]['docID']:
            j += 1
        else:
            i += 1

    return merged

# Returns a merged postings list from 2 separate postings list
# A document is added only when the document IDs are the same.
def merge_postings(postings_1, postings_2):
    merged = []
    i = 0
    j = 0
    while i < len(postings_1) and j < len(postings_2):
        if postings_1[i]['docID'] == postings_2[j]['docID']:
            merged.append(postings_1[i])
            i += 1
            j += 1
        elif postings_1[i]['docID'] > postings_2[j]['docID']:
            j += 1
        else:
            i += 1
    
    return merged

postings = open(postings_file, "rb")
offsets = readDict(dictionary_file)

readQueries(file_of_queries, offsets, postings, [])
