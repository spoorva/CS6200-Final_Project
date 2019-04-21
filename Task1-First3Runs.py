import Indexer
import io
import os
import math
import string
from collections import Counter

# GLOBAL CONSTANTS
CURRENT_DIR = os.getcwd()

ps = string.punctuation
trans = str.maketrans(ps, "                                ")
OUTPUT_DIR = "Outputs/"
DOC_TOKEN_COUNT = {}
INVERTED_INDEX = {}
QUERY_ID = 0

with open("common_words", 'r') as f:
    STOP_WORDS = f.read().splitlines()


def avg_doc_len():
    # Returns the average document length for the documents in this input corpus
    total_length = 0
    for doc in DOC_TOKEN_COUNT:
        total_length += DOC_TOKEN_COUNT[doc]

    return float(total_length) / float(len(DOC_TOKEN_COUNT))


def query_index(sent_q):
    q_words = sent_q.lower().split()
    index = {}
    for word in q_words:
        if word in INVERTED_INDEX:
            index[word] = INVERTED_INDEX[word]
        else:
            index[word] = {}

    return index


def read_rel_info():
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


def rel_doc_count(docs_with_term, relevant_docs):
    count = 0
    for doc_id in docs_with_term:
        if doc_id in relevant_docs:
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

    # return doc scores
    return DOC_SCORE


def QLM_score(new_q):
    # Computes QLM scores for all documents in the given index
    # Returns a map of the document ids with their QLM score

    DOC_SCORE_QLM = {}
    C = 0
    lambda_value = 0.35
    new_q_index = query_index(new_q)

    # Initialize all docs with score = 0
    for doc in DOC_TOKEN_COUNT:
        # DOC_SCORE_QLM[doc] = 0
        C = C + DOC_TOKEN_COUNT[doc]  # total number of words in collection

    for query_term in new_q.split():
        cq = 0
        for doc in new_q_index[query_term]:
            cq = cq + new_q_index[query_term][doc]  # total occurrence of query term in collection

        for doc in new_q_index[query_term]:
            D = DOC_TOKEN_COUNT[doc]  # total number of words in doc
            fq = new_q_index[query_term][doc]  # total occurrence of query term in doc
            first_part = float(1 - lambda_value) * (fq / D)
            second_part = float(lambda_value) * (cq / C)
            if doc in DOC_SCORE_QLM:
                DOC_SCORE_QLM[doc] += math.log(first_part + second_part)
            else:
                DOC_SCORE_QLM[doc] = math.log(first_part + second_part)

    # return doc scores in descending order.
    return DOC_SCORE_QLM


def tfidf_score(new_q):
    # Computes tf-idf scores for all documents in the given index
    # Returns a map of the document ids with their tfidf score

    DOC_SCORE_TFIDF = {}
    tf_idf_dict = {}
    new_q_index = query_index(new_q)

    for term in new_q_index:
        idf = 1.0 + math.log(float(len(DOC_TOKEN_COUNT)) / float(len(new_q_index[term].keys()) + 1))
        for doc_id in new_q_index[term]:
            tf = float(new_q_index[term][doc_id]) / float(DOC_TOKEN_COUNT[doc_id])
            if term not in tf_idf_dict:
                tf_idf_dict[term] = {}
            tf_idf_dict[term][doc_id] = tf * idf

    for term in new_q_index:
        for doc in new_q_index[term]:
            doc_weight = 0
            doc_weight = doc_weight + tf_idf_dict[term][doc]  # get_doc_weight(doc,fetched_index,tf_idf_dict)
            if doc in DOC_SCORE_TFIDF:
                doc_weight = doc_weight + DOC_SCORE_TFIDF[doc]
            DOC_SCORE_TFIDF.update({doc: doc_weight})

    # return doc scores
    return DOC_SCORE_TFIDF


def write_to_file(doc_scores, q_id, output_file):
    # Write output scores to a text file

    rank = 0
    with open(OUTPUT_DIR + output_file + ".txt", "a+") as out_file:
        # Counter(doc_scores).most_common(100):
        sorted_scores = [(k, doc_scores[k]) for k in sorted(doc_scores, key=doc_scores.get, reverse=True)]
        for i in range(1, min(len(sorted_scores), 101)):
            doc, score = sorted_scores[i]
            rank += 1
            out_file.write(str(q_id) + " Q0 " + doc + " " + str(rank) + " " + str(score) + " " + output_file + "\n")


if __name__ == '__main__':
    Indexer.unigram_index(False)
    INVERTED_INDEX = Indexer.INVERTED_INDEX
    DOC_TOKEN_COUNT = Indexer.DOC_TOKEN_COUNT

    models = ["BM25RelevanceRun", "TFIDFRun", "QLRun"]
    for model in models:
        if os.path.exists(OUTPUT_DIR + model + ".txt"):
            os.remove(OUTPUT_DIR + model + ".txt")

    query_file = open("cacm.query.txt", 'r')
    queries = []
    query = ""
    for line in query_file.readlines():
        if line == "\n":
            continue
        if line.startswith("<DOCNO>") or line.startswith("<DOC>"):
            continue
        if line.startswith("</DOC>"):
            queries.append(query.strip().lower())
            query = ""
            continue
        query += " " + line.rstrip("\n").strip().translate(trans)

    for q in queries:
        QUERY_ID += 1
        scores = BM25_score(q)
        OUTPUT_FILE = models[0]
        write_to_file(scores, QUERY_ID, OUTPUT_FILE)

        scores = tfidf_score(q)
        OUTPUT_FILE = models[1]
        write_to_file(scores, QUERY_ID, OUTPUT_FILE)

        scores = QLM_score(q)
        OUTPUT_FILE = models[2]
        write_to_file(scores, QUERY_ID, OUTPUT_FILE)

        print("Completed Retrieval for query : " + q)

    print("End of Retrieval.")
