from collections import Counter
import string
import Indexer
import math
import os

ps = string.punctuation
trans = str.maketrans(ps, "                                ")
INVERTED_INDEX = {}
QUERY_ID = 0
OUTPUT_FILE = "Outputs/StoppedIndexWithBM25.txt"

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


def calc_dice(sent_q, n):
    index_q_words = query_index(sent_q)
    dice_coeffs = {}

    for term, t_files in INVERTED_INDEX.items():
        temp_dc = []
        for q_term, q_files in index_q_words.items():
            # Using Dice coefficient formula -> (2 * Nab)/(Na+Nb)
            n_a = len(t_files)
            n_b = len(q_files)
            n_ab = len(set(t_files).intersection(q_files))
            temp_dc.append((2 * n_ab) / (n_a + n_b))

        dice_coeffs[term] = sum(temp_dc) / len(temp_dc)

    sorted_dice = sorted(dice_coeffs.items(), key=lambda kv: kv[1], reverse=True)
    high_assoc = []
    for w in sorted_dice[0:n]:
        high_assoc.append(w[0])

    return high_assoc


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


def write_to_file(doc_scores, q_id, model):
    # Write output scores to a text file

    rank = 0
    with open("Outputs/" + model + ".txt", "a+") as out_file:
        # Counter(doc_scores).most_common(100):
        sorted_scores = [(k, doc_scores[k]) for k in sorted(doc_scores, key=doc_scores.get, reverse=True)]
        for i in range(1, min(len(sorted_scores), 101)):
            doc, score = sorted_scores[i]
            rank += 1
            out_file.write(str(q_id) + " Q0 " + doc + " " + str(rank) + " " + str(score) + " " + model + "\n")


if __name__ == '__main__':

    Indexer.unigram_index(True)
    INVERTED_INDEX = Indexer.INVERTED_INDEX
    DOC_TOKEN_COUNT = Indexer.DOC_TOKEN_COUNT

    models = ["StoppedIndexWithBM25", "StoppedIndexWithTFIDF"]
    for model in models:
        OUTPUT_FILE = "Outputs/" + model + ".txt"
        if os.path.exists(OUTPUT_FILE):
            os.remove(OUTPUT_FILE)

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

        new_q = ""
        for w in q.split():
            if w not in STOP_WORDS:
                new_q += " " + w

        # Calculating BM25 scores for the stopped query
        scores = BM25_score(new_q)
        model = models[0]
        write_to_file(scores, QUERY_ID, model)

        scores = tfidf_score(new_q)
        model = models[1]
        write_to_file(scores, QUERY_ID, model)

        print("Completed retrieval for - query", QUERY_ID, q)
