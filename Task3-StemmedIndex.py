import math
import os
import re
from collections import Counter

index = {}
inverted_index = {}

DOC_TOKEN_COUNT = {}
INVERTED_INDEX = {}

QUERY_ID = 0


def query_index(sent_q):
    q_words = sent_q.lower().split()
    index = {}
    for word in q_words:
        if word in INVERTED_INDEX:
            index[word] = INVERTED_INDEX[word]
        else:
            index[word] = {}

    return index


def get_corpus():
    with open("cacm_stem.txt", "r") as file:
        text = ""
        lines = file.readlines()
        for i in range(0, len(lines)):
            line = lines[i]
            if line[0] == "#":
                j = i + 1
                doc_id = line[2:]
                while "#" not in lines[j]:
                    text = text + lines[j]
                    j = j + 1

                    if j >= len(lines):
                        break

                match = re.search(r'\sam|\spm', text)

                if match:
                    index[int(doc_id.strip())] = text[:match.end() - 2].split()

                text = ""
    return index


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


def avg_doc_len():
    # To calculate the average document length for the documents in this input corpus
    tot_length = 0
    for doc in DOC_TOKEN_COUNT:
        tot_length += DOC_TOKEN_COUNT[doc]

    return float(tot_length) / float(len(DOC_TOKEN_COUNT))


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


def write_to_file(scores, q_id, model):
    rank = 0
    with open("Outputs/" + model + ".txt", "a+") as out_file:
        sorted_scores = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
        for i in range(1, min(len(sorted_scores), 101)):
            doc, score = sorted_scores[i]
            rank += 1
            out_file.write(str(q_id) + " Q0 " + str(doc) + " " + str(rank) + " " + str(score) + " " + model + "\n")


if __name__ == '__main__':

    index = get_corpus()

    for key, value in index.items():
        for v in value:
            inverted_index.setdefault(v, []).append(key)

    for k, v in inverted_index.items():
        INVERTED_INDEX[k] = Counter(v)

    for key, value in index.items():
        DOC_TOKEN_COUNT[key] = len(value)

    with open("cacm_stem.query.txt", "r") as file:
        queries = file.readlines()

    models = ["StemmingWithBM25", "StemmingWithTFIDF"]
    for model in models:
        OUTPUT_FILE = "Outputs/" + model + ".txt"
        if os.path.exists(OUTPUT_FILE):
            os.remove(OUTPUT_FILE)

    for query in queries:
        QUERY_ID += 1

        # Compute ranking scores of all docs for this query using BM25.
        doc_scores = BM25_score(query)
        write_to_file(doc_scores, QUERY_ID, models[0])

        # Compute ranking scores of all docs for this query using TFIDF.
        doc_scores = tfidf_score(query)
        write_to_file(doc_scores, QUERY_ID, models[1])
