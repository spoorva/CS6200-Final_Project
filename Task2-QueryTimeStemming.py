from bs4 import BeautifulSoup
import requests
import corpusGeneration
import Indexer
import os
import math
from collections import Counter

INVERTED_INDEX = {}
QUERY_ID = 0
OUTPUT_FILE = "Outputs/QueryTimeStemWithBM25.txt"

with open("common_words", 'r') as f:
    STOP_WORDS = f.read().splitlines()


def query_index(sent_q):
    q_words = sent_q.lower().split()
    index = {}
    for word in q_words:
        if word in INVERTED_INDEX:
            index[word] = INVERTED_INDEX[word]
        else:
            index[word] = {}

    return index


def avg_doc_len():
    # To calculate the average document length for the documents in this input corpus
    tot_length = 0
    for doc in DOC_TOKEN_COUNT:
        tot_length += DOC_TOKEN_COUNT[doc]

    return float(tot_length) / float(len(DOC_TOKEN_COUNT))


def read_rel_info():
    rel_docs = []
    rel_docs_in_corpus = []
    with open("cacm.rel.txt", 'r', encoding="utf-8") as rel_file:
        for rel_line in rel_file.readlines():
            values = rel_line.split()
            if values and (values[0] == str(QUERY_ID)):
                rel_docs.append(values[2])
        for doc_id in DOC_TOKEN_COUNT:
            if doc_id in rel_docs:
                rel_docs_in_corpus.append(doc_id)

    return rel_docs_in_corpus


def rel_doc_count(docs_with_term, rel_docs):
    count = 0
    for doc_id in docs_with_term:
        if doc_id in rel_docs:
            count += 1
    return count


def BM25_score(new_q):
    # Computes BM25 scores for all documents in the given index
    # Returns a map of the document ids with their BM25 score
    new_q = new_q.lower()
    DOC_SCORE = {}
    rel_docs = read_rel_info()
    R = len(rel_docs)
    q_tf = Counter(new_q.split())
    new_q_index = query_index(new_q)

    avdl = avg_doc_len()
    N = len(DOC_TOKEN_COUNT)
    k1 = 1.2
    k2 = 100
    b = 0.75

    for query_term in new_q.split():
        qf = q_tf[query_term]
        n = len(new_q_index[query_term])
        if query_term in INVERTED_INDEX:
            r = rel_doc_count(INVERTED_INDEX[query_term], rel_docs)
        else:
            r = 0
        dl = 0
        for doc in new_q_index[query_term]:
            f = new_q_index[query_term][doc]
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


def write_to_file(doc_scores, q_id):
    # Write output scores to a text file

    rank = 0
    with open(OUTPUT_FILE, "a+") as out_file:
        # Counter(doc_scores).most_common(100):
        sorted_scores = [(k, doc_scores[k]) for k in sorted(doc_scores, key=doc_scores.get, reverse=True)]
        for i in range(1, min(len(sorted_scores), 101)):
            doc, score = sorted_scores[i]
            rank += 1
            model = "QueryTimeStemWithBM25"
            out_file.write(str(q_id) + " Q0 " + doc + " " + str(rank) + " " + str(score) + " " + model + "\n")


if __name__ == '__main__':
    # Creating unstopped index from Indexer.py
    Indexer.unigram_index(False)
    INVERTED_INDEX = Indexer.INVERTED_INDEX
    DOC_TOKEN_COUNT = Indexer.DOC_TOKEN_COUNT

    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

    query = {}
    count = 1
    query_text = open("cacm.query.txt", 'r')
    q_soup = BeautifulSoup(query_text, 'html.parser')
    q_soup.prettify().encode('utf-8')
    for text in q_soup.findAll('docno'):
        text.extract()
    for text in q_soup.findAll('doc'):
        queries = text.get_text().strip(' \n\t')
        queries = str(queries)
        queries = queries.lower()
        queries = corpusGeneration.text_transformation(queries)
        query[count] = queries.split(" ")

        for i in STOP_WORDS:
            if i in query[count]:
                query[count].remove(i)

        str1 = "  ".join(str(e) for e in query[count])

        headers = {"X-RapidAPI-Host": "wordsapiv1.p.rapidapi.com",
                   "X-RapidAPI-Key": "3d91b5b661mshc5033075a07e3bap1c57bbjsnef1bff5d543d"}

        derivatives = set()
        for term in query[count]:
            response = requests.get('https://wordsapiv1.p.mashape.com/words/' + term, headers=headers)
            if 'results' in response.json():
                for resp in (response.json().get('results')):
                    if response.json().get('results') is not None and resp is not None and 'derivation' in resp:
                        for i in resp['derivation']:
                            # Adding derivatives to original query
                            derivatives.add(i)

        for w in derivatives:
            query[count].append(w)
        print("Completed expansion of query", count)
        count = count + 1

    for q in query.values():
        QUERY_ID += 1
        new_q = " ".join(q)
        scores = BM25_score(new_q)
        write_to_file(scores, QUERY_ID)
