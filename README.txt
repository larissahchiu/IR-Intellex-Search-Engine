== Python Version ==

We're using Python Version <3.6.6> for this assignment.

== General Notes about this assignment ==

Give an overview of your program, describe the important algorithms/steps
in your program, and discuss your experiments in general.  A few paragraphs
are usually sufficient.

Indexing (index.py)
1.Load training data from the specified dataset. With the given dataset, we decide to only index the content portion of each document.
2.For each line of a document, the following preprocessing is done:
	1. Split the line into its constituent tokens
	2. Convert all tokens to lowercase
	3. Remove number tokens
	4. Remove punctuation tokens.
	5. Remove stop word tokens.
	6. Word tokens are then stemmed and any punctuation is removed from them.
3. After preprocessing, the position of each token is then added to the dictionary for that line.
4. The line's dictionary is then merged with the document's dictionary, which has the following structure:
dictionary: {
	token1: {
		docID: [1, 5, 7, ...]
	},
	token2: {
		docID: [2, 4, 8, ...]
	},
	...
}
5. After all the document's lines are processed, the length of each document is calculated using the length of each positional postings list for each token
in the document's dictionary. The length is then stored into a lengths dictionary which will be later pickled to 'lengths.txt'.
6. For each token, compute a normalised logtf for each docID found in each token's postings. The frequency is stored as a key `freq` in the document's dictionary.
7. The dictionary is then sorted and the tokens and their specified byte offsets (for their postings list) are written into the specified dictionary file.
The postings are also sorted according to normalised logtf.
8. The postings are then pickled into the specified postings file.

Searching (search.py):
1. Opens the postings.txt file
2. Generates a dictionary with tokens as keys and byte offsets as values.
3. Obtains a list of all document IDs from all the documents present in the corpora folder.
4. Evaluates each query from the specified query file as follows:
	1. Reads the query, and determines if it is a phrasal query or boolean query
	    - For both types of queries, we then expand the query. Refer to the improvements section below to see how we've expanded our queries
	2. Evaluate the expression provided by the `parse` method
	    - If the query contains a boolean, we parse the boolean query by seperating the query into the
	    different ngrams and then weight the ngrams in the query
	    - If the query is just a standard phrasal query, we parse it normally with stemming
	3. After we have parsed the queries, we evaluate the necessary documents using
	the tf-idf scoring.
	    - Inside the 'cosine_score' method, we first determine the query scores by performing
	    tf-idf scoring with normalization.
	    - Then for each of the terms in the query, we obtain the postings lists and calculate
	    the weights through the stored tf weight stored in the posting list
	    - Then we perform normalization on the scores of each document
	    - We then build a max heap with the maximum score at the top
5. The result from each query is then written into the specified results file.

Query expansion (query_expansion.py):
The idea is to expand the query using thesaurus. For each term in the query, find the synonym using the thesaurus, append them to the original query and then proceed to search.

1.expand_query_free:
replace each word in the free text query with synonyms for that word; return a list of expanded queries.
For eg:
'good bad' = ['excel bad', 'excellent bad', 'merit bad', 'good abysmal', 'good worst']

2.expand_query_boolean:
replace each word in the boolean query with synonyms for that word; return a list of expanded queries.
For eg:
'good AND bad' = ['excel AND bad', 'excellent AND bad', 'good AND abysmal', 'good AND worst']

heap.py:
1.An implementation of standard binary heap, using an array.
2.But, binary heap will be built using a dictionary instead of an array.
3.Heap will be used to get the top K documents for a given query.


3. limitation:
This approach is less useful when users themselves are unsure about the query. As in the expansion can only find synonyms word by word, it cannot abstract out ideas from free text and extend the query. A possible improvement would be utilising pseudo relevance feedback, which is to find key terms from the first retrieved documents and do search again based on them.


== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

index.py [Code for indexing the corpus]
search.py [Code for searching through the corpus]
dictionary.txt [generated dictionary file containing tokens as keys and byte offsets as values]
postings.txt [pickled postings lists for each token, uses positional indexes]
relevance_feedback.py [contains the rocchio formula implementation for relevance feedback]
query_expansion.py [contains query expansion methods]

== Improvements ==

We implemented certain query expansion techniques to improve our system; specifically, we focused on
using the nltk's wordnet interface to extract synsets. The synsets is a set of synonyms that we would then add to our query
to make our expanded query list. So instead of answering 1 free text or boolean query, we are able to
answer multiple free text or boolean queries, so that we could mine for more relevant documents.

We used the sample queries provided in IVLE which had some expert relevance assessments provided.

Results:
Without query expansion:

Query: quiet phone call
Precision: 0.0002476
Recall: 1

Query: good grades exchange scandal
Precision: 0.0001822
Recall: 1

Query: "fertility treatment" AND damages
Precision: 0.375
Recall: 1

With query expansion:

Query: quiet phone call
Precision: 0.0002476
Recall: 1

Query: good grades exchange scandal
Precision: 0.0001822
Recall: 1

Query: "fertility treatment" AND damages
Precision: 0.0005298
Recall: 1

In general, the results are similar, except for the last query where the precision was greatly reduced due to the large amount of documents returned by the algorithm. In addition,
the results provided by the query expansion enabled engine ranked the relevant documents much lower than that of the engine without query expansion. As such, we have decided to turn off
the enhancement for the final submission as we do not think it improves the retrieval of the documents.
