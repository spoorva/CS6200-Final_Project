from collections import Counter
from collections import defaultdict
import string
import Indexer
import math
import os

ps = string.punctuation
trans = str.maketrans(ps, "                                ")
INVERTED_INDEX = {}
DOC_TOKEN_COUNT = 0
QUERY_ID = 0
OUTPUT_FILE = "Outputs/ExtraCredit_KL_Div.txt"

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


def KL_div_score(new_q):
    # Computes the KL_Divergence score
    new_q = new_q.lower()

    DOC_SCORE_KL = defaultdict(lambda: 0.0)  # initialise the values of the dict to 0.0

    q_tf = Counter(new_q.split())
    new_q_index = query_index(new_q)
    dl = 0
    Q = len(new_q)  # This gives the length of the Passed Query which will be used later in the formula

    for query_term in new_q.split():
        qf = q_tf[query_term]   # query_frequency
        
        for doc in new_q_index[query_term]:
            if doc in DOC_TOKEN_COUNT:
                dl = DOC_TOKEN_COUNT[doc]  # This is the length of that document

            freq = new_q_index[query_term][doc]

            # Compute the score as : P(w|Q).log(P(W|D))
            score = float((qf/Q) * math.log(freq/dl))
            DOC_SCORE_KL[doc] += score

    # return doc scores
    return DOC_SCORE_KL


def write_to_file(doc_scores, q_id):
    # Write output scores to a text file
    rank = 0
    with open(OUTPUT_FILE, "a+") as out_file:
        # Counter(doc_scores).most_common(100):
        sorted_scores = [(k, doc_scores[k]) for k in sorted(doc_scores, key=doc_scores.get, reverse=True)]
        for i in range(1, min(len(sorted_scores), 101)):
            doc, score = sorted_scores[i]
            rank += 1
            model = "PseudoRelevanceWithKL_Divergence"
            out_file.write(str(q_id) + " Q0 " + doc + " " + str(rank) + " " + str(score) + " " + model + "\n")


if __name__ == '__main__':

    Indexer.unigram_index(False)
    INVERTED_INDEX = Indexer.INVERTED_INDEX
    DOC_TOKEN_COUNT = Indexer.DOC_TOKEN_COUNT
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

    high_assoc_q = []
    for q in queries:
        QUERY_ID += 1
        high_assoc_q = calc_dice(q, 7)

        # Add high assoc terms to query
        for w in high_assoc_q:
            # if the word is not equal to the query, then add it to the query
            if w not in q:
                q += " " + w

        # Calculating KL Divergence scores for the stopped query
        scores = KL_div_score(q)
        write_to_file(scores, QUERY_ID)

        print("Completed retrieval for - query", QUERY_ID, q)
