import io
import math
import os
import re
import pdb
import sys
import traceback
from collections import Counter
import corpusGeneration
import nltk

index = {}
inverted_index = {}

CURRENT_DIR = os.getcwd()

RUN_OUTPUTS_DIR = os.path.join(CURRENT_DIR, "Outputs")

DOC_TOKEN_COUNT = {}
INVERTED_INDEX = {}

QUERY_ID = 0

def get_corpus():
    with open("C:\\Users\\Poorva\\Downloads\\test-collection\\cacm_stem.txt", "r") as file:

        j = 0
        text = ""
        lines = file.readlines()
        for i in range(0, len(lines)):

            line = lines[i]

            if line[0] == "#":

                j = i + 1

                docid = line[2:]

                while "#" not in lines[j]:

                    text = text + lines[j]
                    j = j + 1

                    if (j >= len(lines)):
                        break;

                match = re.search(r'\sam|\spm', text)

                if match:
                    index[int(docid.strip())] = text[:match.end() - 2].split()

                text = ""


def read_relevance_info():
    try:
        relevant_docs = []
        rel_docs_in_corpus = []
        with io.open("cacm.rel.txt", 'r', encoding="utf-8") as relevance_file:

            for line in relevance_file.readlines():
                values = line.split()
                if values and (values[0] == str(QUERY_ID)):
                    relevant_docs.append(values[2])
            for doc_id in DOC_TOKEN_COUNT:
                if doc_id in relevant_docs:
                    rel_docs_in_corpus.append(doc_id)

        return rel_docs_in_corpus
    except Exception as e:
        print(traceback.format_exc())


def average_doc_length():
    """Returns the average document length for the documents in this input corpus."""

    total_length = 0
    for doc in DOC_TOKEN_COUNT:
        total_length += DOC_TOKEN_COUNT[doc]

    return float(total_length) / float(len(DOC_TOKEN_COUNT))


def relevant_doc_count(docs_with_term, relevant_docs):
    count = 0
    for doc_id in docs_with_term:
        if doc_id in relevant_docs:
            count += 1
    return count


def BM25_score(fetched_index, query_term_freq):
    """Computes BM25 scores for all documents in the given index.
    Returns a map of the document ids with thier BM25 score."""

    DOC_SCORE = {}

    # Initialize all docs with score = 0
    # for doc in DOC_TOKEN_COUNT:
    #    DOC_SCORE[doc] = 0

    relevant_docs = read_relevance_info()
    R = len(relevant_docs)

    avdl = average_doc_length()
    N = len(DOC_TOKEN_COUNT)
    k1 = 1.2
    k2 = 100
    b = 0.75

    for query_term in query_term_freq:

        qf = query_term_freq[query_term]
        n = len(fetched_index[query_term])
        if query_term in INVERTED_INDEX:
            r = relevant_doc_count(INVERTED_INDEX[query_term], relevant_docs)
        else:
            r = 0
        dl = 0
        for doc in fetched_index[query_term]:

            f = fetched_index[query_term][doc]
            if doc in DOC_TOKEN_COUNT:
                dl = DOC_TOKEN_COUNT[doc]
            K = k1 * ((1 - b) + (b * (float(dl) / float(avdl))))
            relevance_part = math.log(((r + 0.5) / (R - r + 0.5)) / ((n - r + 0.5) / (N - n - R + r + 0.5)))
            k1_part = ((k1 + 1) * f) / (K + f)
            k2_part = ((k2 + 1) * qf) / (k2 + qf)
            if doc in DOC_SCORE:
                DOC_SCORE[doc] += (relevance_part * k1_part * k2_part)
            else:
                DOC_SCORE[doc] = (relevance_part * k1_part * k2_part)

    # return doc scores in descending order.
    return DOC_SCORE


def query_term_freq_map(query):
    """Returns a map of query terms and their corresponding frequency in the query."""

    query_terms = query.split()
    query_term_freq = {}
    for term in query_terms:
        if term not in query_term_freq:
            query_term_freq[term] = 1
        else:
            query_term_freq[term] += 1
    return query_term_freq


def query_matching_index(query_term_freq):
    """Fetches only those inverted lists from the index, that correspond to the query terms."""

    fetched_index = {}
    for term in query_term_freq:
        if term in INVERTED_INDEX:
            fetched_index[term] = INVERTED_INDEX[term]
        else:
            fetched_index[term] = {}

    return fetched_index


get_corpus()

for key, value in index.items():
    for v in value:
        inverted_index.setdefault(v, []).append(key)


for k, v in inverted_index.items():
    INVERTED_INDEX[k] = Counter(v)

for key, value in index.items():
    DOC_TOKEN_COUNT[key] = len(value)



with open("cacm_stem.query.txt", "r") as file:

    queries = file.readlines()

for query in queries:

        QUERY_ID += 1

        # Dictionary of query term frequency
        query_term_freq = query_term_freq_map(query)

        # Fetch the inverted indexes corresponding to the terms
        # in the query.
        fetched_index = query_matching_index(query_term_freq)

        # Compute ranking scores of all docs for this query.
        doc_scores = BM25_score(fetched_index, query_term_freq)

        # for key, value in doc_scores.items():
        #     print(key, ":", value)

        f = open("stemmed_" + query.strip() + ".txt", "w")
        for key, val in sorted(doc_scores.items(), key=lambda kv: kv[1], reverse=True):

            f.write(str(key) +  " : " + str(val))
            f.write("\n")






