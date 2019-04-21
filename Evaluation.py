import os
from tabulate import tabulate

OUTPUT_DIR = "Evaluation/"
OUTPUT = []


def evaluation(run, file):
    rel_jdmt_docs = {}
    query_doc = {}
    queries = []
    rel_doc = {} 

    cacm_rel = open("cacm.rel.txt", "r")
    # Creates a rel_jdmt_docs dictionary that maps the query to the total number of relevant documents
    for line in cacm_rel:
        elements = line.split()
        if elements[0] in rel_jdmt_docs:
            rel_jdmt_docs[elements[0]] += 1
        else:
            rel_jdmt_docs[elements[0]] = 1

        # Creates a dictionary rel_doc that maps the doc and query to the relevance judgement for that
        # query for that term.
        rel_doc[elements[0] + elements[2]] = elements[3]
    cacm_rel.close()

    if os.path.exists(OUTPUT_DIR + run + "_result.txt"):
        os.remove(OUTPUT_DIR + run + "_result.txt")

    # Creates a file with the output retrieval model name+"result.txt"
    out_file = open(OUTPUT_DIR + run + "_result.txt", "w")
    # The format in which the outputs are required.
    out_file.write("Query \t Document \t Ranking \t R/N \t Precision \t\tRecall" + "\n")
    in_file = open(file, "r")
    # Computes all the queries and stores it in queries.
    for line in in_file:
        temp = line.split()
        if not (temp[0] in queries):
            queries.append(temp[0])
        # A dictionary consisting of query to doc mapping is generated only if relevance judgements 
        # for that query is present, other queries are just skipped.
        if temp[0] in rel_jdmt_docs:
            if temp[0] in query_doc:
                query_doc[temp[0]].append(temp[2])
            else:
                query_doc[temp[0]] = [temp[2]]
    retrieved, relevant, precision, recall, avg_prec = {}, {}, {}, {}, {}
    total_rel, prec_5, prec_20, file_not_evaluated, rr = {}, {}, {}, {}, {}
    mp, mrr, flag = 0, 0, {}

    # Initializing the dictionaries for all docs in query_doc dictionary
    for i, tokens in query_doc.items():
        retrieved[i], precision[i], recall[i], relevant[i] = 0, 0, 0, 0
        avg_prec[i], flag[i], rr[i], prec_5[i], prec_20[i] = 0, 0, 0, 0, 0
        file_not_evaluated[i] = False

        if i not in rel_jdmt_docs:
            file_not_evaluated[i] = True

    # Calculating the total number for relevant documents for all queries.
    for i, tokens in rel_jdmt_docs.items():
        total_rel[i] = tokens

    # Computing precision, recall, precision at 5, precision at 20, reciprocal ranking and average precision
    # for all the queries.
    for i, tokens in query_doc.items():
        for token2 in tokens:
            retrieved[i] = retrieved[i] + 1
            rn = "N"
            # If document for a query is relevant and is the first relevant document, compute reciprocal rank.
            if (i + token2) in rel_doc:
                if flag[i] == 0:
                    rr[i] = 1 / retrieved[i]
                    flag[i] = 1
                relevant[i] = relevant[i] + 1
                rn = "R"

                avg_prec[i] = avg_prec[i] + float(relevant[i]) / float(retrieved[i])

            precision[i] = round(float(relevant[i]) / float(retrieved[i]), 2)
            recall[i] = round(float(relevant[i]) / float(total_rel[i]), 2)

            if retrieved[i] == 5:
                prec_5[i] = precision[i]
            if retrieved[i] == 20:
                prec_20[i] = precision[i]

            # Prints the output to a file
            out_file.write(str(i) + "\t\t " + str(token2) + "\t\t" + str(retrieved[i]) + "\t\t  " + str(
                rn) + " \t\t%.2f" % precision[i] + "\t\t %.2f" % recall[i] + "\n")
        out_file.write("P@5 for query " + str(i) + " is: " + str(prec_5[i]) + "\n")
        out_file.write("P@20 for query " + str(i) + " is: " + str(prec_20[i]) + "\n")
    out_file.close()

    # Computes map and mrr for all the queries
    for query in queries:
        if query in rel_jdmt_docs:
            mp = mp + (float(avg_prec[query]) / float(total_rel[query]))
            mrr = mrr + rr[query]

    out_file = open(OUTPUT_DIR + run + "_MAP_MRR_Result.txt", "w")
    mp = float(mp) / 64
    mrr = float(mrr) / 64

    # Prints the output in a separate file
    out_file.write("MAP for " + str(run) + " is: " + str(mp) + "\n")
    out_file.write("MRR for " + str(run) + " is: " + str(mrr) + "\n")

    out_file.close()
    OUTPUT.append([run, mp, mrr])


if __name__ == '__main__':

    with open("Output_files_list.txt", 'r') as file_list:
        files = file_list.readlines()

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    f_out = open("Evaluation/MAP_MRR_Evaluation_Summary.txt", 'w')
    for line in files:
        run, file = line.strip().split("\t")
        evaluation(run, file)

    f_out.write(tabulate(OUTPUT, headers=["System Name", "MAP", "MRR"], showindex=True))
