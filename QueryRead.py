from bs4 import BeautifulSoup
import corpusGeneration


# Function to read query file and parse it
def read_query_file():
    query = {}
    count = 1
    query_text = open('cacm.query.txt', 'r')
    q_soup = BeautifulSoup(query_text, 'html.parser')
    q_soup.prettify().encode('utf-8')
    for text in q_soup.findAll('docno'):
        text.extract()
    for text in q_soup.findAll('doc'):
        queries = text.get_text().strip(' \n\t')
        queries = str(queries)
        queries = queries.lower()
        queries = corpusGeneration.text_transformation(queries)
        # write_to_file(count, queries)
        query[count] = queries.split(" ")
        count += 1

    return query


# Function to read stopwords file
def stop_words():
    stopwords = []
    for items in open('common_words', 'r').readlines():
        stopwords.append(items.strip("\n"))
    return stopwords


# Function to read relevance judgement file
def relevant_set():
    relevant = {}
    for line in open("cacm.rel", 'r'):
        lines = line.split(" ")
        if relevant.has_key(lines[0]):
            relevant[lines[0]] += [lines[2] + ".txt"]
        else:
            relevant[lines[0]] = [lines[2] + ".txt"]

    for i in xrange(1, 65):
        if relevant.has_key(str(i)):
            pass
        else:
            relevant[str(i)] = []
    return relevant


# Function to write queries in the file in a specific format for Lucene
def write_to_file(qid, query):
    if qid == 1:
        with open("Query.txt", 'w') as f:
            f.write(str(qid) + " " + query + "\n")
    else:
        with open("Query.txt", 'a') as f:
            f.write(str(qid) + " " + query + "\n")
