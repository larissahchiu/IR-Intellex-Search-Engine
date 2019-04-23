import pandas as pd
import re
import nltk
import sys
import getopt
import os
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import _pickle as cPickle
import math

set_stopwords = set(stopwords.words('english'))
punc = "()[.',?!\";:-]/+>$“*…^`‘’&–@”#—%<=_\\"
eng_alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']


#initialised inverted_index, key == words, value = posting list
inverted_index = {}

#for development purposes
dataset_dir = 'C:/Users/Wei Chin/Desktop/CS3245/HW #2/dataset.csv'

def remove_stopword_punc_token(token_list):
    #for loop to literate token_list to remove: stopword tokens from token_list and punc tokens
    for token in token_list:
        #remove stopword token or punc token
        if token in set_stopwords or token in punc:
            token_list.remove(token)

    return token_list

#do stemming and removing punctuation from token
def remove_punc_from_token(token_list,stemmer):
    #for loop to literate token_list to remove punctuation from token
    for i in range(len(token_list)):
        curr_token = token_list[i]
        #if punc occurs in a token
        if any(char in punc for char in curr_token):
            #create a new token without punc
            new_curr_token = ''.join(char for char in curr_token if char not in punc)
            #replace old token with punc with new token w/o punc
            new_curr_token = stemmer.stem(new_curr_token)
            token_list[i] = new_curr_token
        else:
            curr_token = stemmer.stem(curr_token)
            token_list[i] = curr_token
    return token_list



def process_token_list(token_list, pos, docID):
    #print(token_list)
    ps = PorterStemmer()
    processed_dic = {}
    
    #remove stopword and punc from token_list
    token_list = remove_stopword_punc_token(token_list)
    #remove punc from tokens and stem tokens, return list with punc removed from all tokens
    token_list = remove_punc_from_token(token_list, ps)
    curr_pos = pos

    for token in token_list:
        if token == ' ':
            continue
        if token in set_stopwords:
            continue
        if token in punc:
            continue
        if any(char.isdigit() for char in token):
            if not any(char for char in token if char in eng_alphabet):
                continue
            else:
                token = ''.join(char for char in token if not char.isdigit())
        if token not in processed_dic:
            processed_dic[token] = [curr_pos]   
        else:
            curr_postings = processed_dic[token]
            curr_postings.append(curr_pos)
        curr_pos += 1
    
    curr_pos += 1
    lst = []
    lst.append(processed_dic)
    lst.append(curr_pos)
    return lst

def process_line(line, pos, docID):
    #convert everything to lowercase
    line = line.lower()
    #tokenize line
    token_list = word_tokenize(line)
    lst = process_token_list(token_list, pos, docID)
    return lst

def process_content(content, docID):
    #since content is multi-line string, we create an iterator for it
    content_iter = iter(content.splitlines())
    #create a word dic for a docID, with the following structure:
    #{ 'I': { docID: [ positions 1,2,3... ] } }
    word_dic_for_doc = {}
    
    pos = 1
    for line in content_iter:
        if line != '\n' or line != ':':
            #get lst = [dictionary for that line, curr_pos + 1]
            lst = process_line(line, pos, docID)
            pos = lst[1]
            dic = lst[0]

            for key in dic:
                if key not in word_dic_for_doc:
                    word_dic_for_doc[key] = {docID : dic[key]}
                else:
                    #get { docID: [positions 1,2,3...] } from word_dic_for_doc
                    curr_dic_doc = word_dic_for_doc[key]
                    #get [positions 1,2,3...] from { docID: [positions 1,2,3...] }
                    existing_positions_post = curr_dic_doc[docID]
                    #get curr positions postings
                    curr_positions_post = dic[key]
                    updated_positions_post = existing_positions_post  + curr_positions_post
                    #update positions post
                    curr_dic_doc[docID] = updated_positions_post


    return word_dic_for_doc 

def process_frequencies(doc_word_dic, docID):
    # logarithm term frequency
    for word in doc_word_dic:
        doc_word_dic[word]['freq'] = 1 + math.log10(len(doc_word_dic[word][docID]))

    # get squared weights
    sum = 0
    for word in doc_word_dic:
        sum += pow(doc_word_dic[word]['freq'], 2)
    
    sum = pow(sum, 0.5)

    # perform normalization on each term
    for word in doc_word_dic:
        doc_word_dic[word]['freq'] = doc_word_dic[word]['freq'] / sum
    
    return doc_word_dic

def populate_index(doc_word_dic, docID):
    for word in doc_word_dic:
        #value == {docID : positions list}
        value = doc_word_dic[word]
        dic = {}
        dic['docID'] = docID
        dic['positions'] = value[docID]
        dic['freq'] = value['freq']
        if word not in inverted_index:
            lst = []
            lst.append(dic)
            inverted_index[word] = lst
        else:
            inverted_index[word].append(dic)

            


def index(data_dir, dic_file, post_file):
    data = pd.read_csv(data_dir)
    #get data with only desired columns
    col = ['document_id', 'content']
    subsetted_data = data[col]
    count = 0
    for row in subsetted_data.iterrows():
        # if count == 2:
        #     break
        row_data = row[1]
        docID = row_data[0]
        print(docID)
        content = row_data[1]
        #process legal content for current docID
        doc_word_dic = process_content(content, docID)
        doc_word_dic = process_frequencies(doc_word_dic, docID)
        #doc_word_dic has the following structure:
        #{I : {1:[1,3,6]} }

        #inverted index will have the following structure:
        #{I : [ {docID: 1, postings:[1,3,6]}, {docID:2, postings:[1,2,3]} ]}
        if len(doc_word_dic) > 0:
            populate_index(doc_word_dic, docID)
        count += 1

    d_f = open(dic_file, 'w+', encoding='utf-8')
    # p_f = open('p_readable.txt', 'w+')
    p_pickle_f = open(post_file, 'wb')

    for term in sorted(inverted_index.keys()):
        
        line_df = term + ' ' +  str(p_pickle_f.tell())  + '\n'
        d_f.write(line_df)
        #write posting values and is human-readable
        lst = inverted_index[term]
        line_pf = str(lst)
        # p_f.write(line_pf + '\n')
        cPickle.dump(lst, p_pickle_f)
    d_f.close()
    # p_f.close()
    p_pickle_f.close()


def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")


input_directory = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')

except getopt.GetoptError as err:
    usage()
    sys.exit(2)
    
for o, a in opts:
    if o == '-i': # input directory
        input_directory = a
    elif o == '-d': # dictionary file
        output_file_dictionary = a
    elif o == '-p': # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if input_directory == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)
index(input_directory, output_file_dictionary, output_file_postings)