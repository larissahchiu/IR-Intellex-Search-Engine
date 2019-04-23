import nltk
from nltk.corpus import wordnet
from nltk.stem.porter import *
from nltk.stem.porter import *
import re

ps = PorterStemmer()
punc = "()[.,?!'\";:-]/+>$*^`&"
def process_1st_word(first_word, word_set):
    syn_list = wordnet.synsets(first_word)
    #for loop processes synonyms from syn_list
    word_set = process_syn_list(syn_list)
    return word_set

def process_syn_list(syn_list):
    processed_set = set()
    for word in syn_list:
        #last 5 char of each word is redundant info
        processed_word = word.name()[:-5]
        #remove punctuation

        processed_set.add(processed_word)
    return processed_set


#accepts a free-txt query string
#returns a list of synoynms of the original query
def expand_query_free(ori_query):
    word_list = ori_query.split(' ')
    expanded_query_list = [ori_query]

    for i in range(len(word_list)):
        word_i = word_list[i]
        synonym = wordnet.synsets(word_i)
        syn_set = process_syn_list(synonym)
        syn_list = list(syn_set)

        if i == 0:
            subset = word_list[1:len(word_list)]
            for syn in syn_list:
                new_q = syn + ' ' + ' '.join(subset)
                expanded_query_list.append(new_q)

        elif i > 0 and i < len(word_list)-1:
            subset_prior = word_list[0 : i]
            subset_posterior = word_list[i+1 : len(word_list)]
            for syn in syn_list:
                new_q = ' '.join(subset_prior) + ' ' + syn + ' ' + ' '.join(subset_posterior)
                expanded_query_list.append(new_q)
        else:
            subset_prior = word_list[0:i]
            for syn in syn_list:
                new_q = ' '.join(subset_prior) + ' ' + syn
                expanded_query_list.append(new_q)
    return expanded_query_list

def expand_query_boolean(ori_query):
    word_list = ori_query.split(' ')
    expanded_query_list = [ori_query]

    for i in range(len(word_list)):

        word_i = word_list[i]
        
        if word_i == 'AND':
            continue
        print(word_i)
        synonym = wordnet.synsets(word_i)
        syn_set = process_syn_list(synonym)
        syn_list = list(syn_set)

        if i == 0:
            subset = word_list[1:len(word_list)]
            for syn in syn_list:
                new_q = syn + ' ' + ' '.join(subset)
                expanded_query_list.append(new_q)

        elif i > 0 and i < len(word_list)-1:
            subset_prior = word_list[0 : i]
            subset_posterior = word_list[i+1 : len(word_list)]
            for syn in syn_list:
                new_q = ' '.join(subset_prior) + ' ' + syn + ' ' + ' '.join(subset_posterior)
                expanded_query_list.append(new_q)
        else:
            subset_prior = word_list[0:i]
            for syn in syn_list:
                new_q = ' '.join(subset_prior) + ' ' + syn
                expanded_query_list.append(new_q)
                
    return expanded_query_list



            
    







    
    
    

