import operator
import QueryRead
import snippetCorpusGeneration

# Defining global variables
snippetCorpusGeneration.get_content()
stopwords = QueryRead.stop_words()


# Function to check if the term is present in query or not
def term_in_query(term, query):
    if term.lower() in query.split() and term.lower() not in stopwords:
        return True
    return False


# Function to get first index of significant word window
def get_first_index(sentence, query):
    for term in sentence:
        if term_in_query(term, query):
            return sentence.index(term)


# Function to get last index of significant word window
def get_last_index(sentence, query):
    for index in range(len(sentence) - 1, -1, -1):
        if term_in_query(sentence[index], query):
            return index + 1


# Function to calculate significance factor
# calculates significance factor = (square of no. of significant terms) / total words in significant word window
def calc_significance_factor(sentence, query):
    n_significant_terms = 0

    s = sentence.split()

    first_index = get_first_index(s, query)  # get first index matching query
    last_index = get_last_index(s, query)  # get last index matching query

    for term_in_window in s[first_index: last_index]:
        if term_in_query(term_in_window, query):
            n_significant_terms += 1

    if len(s[first_index: last_index]) == 0:
        return 0.0
    else:
        return round(float(n_significant_terms * n_significant_terms) / len(s[first_index: last_index]), 2)


# Function to generate snippet
def generate_snippet(f, query):
    q_dict = {}
    for lines in open("Phase_1_Output/Task_3a_BM25.txt", 'r').readlines():
        result = lines.split(" ")
        if q_dict.has_key(result[0]):
            q_dict[result[0]] += ["Snippet_Corpus/" + result[2] + ".txt"]
        else:
            q_dict[result[0]] = ["Snippet_Corpus/" + result[2] + ".txt"]

    for each_query in xrange(1, 65):
        each_query = str(each_query)
        sentence_significance_dict = {}

        f.write("Snippet Generation for Query id: " + each_query + "\n\n")

        for corpus_file in q_dict[each_query][:10]:
            # Change the value of index from 10 to desired number of docs for snippet generation in above line
            if not corpus_file.startswith('.'):
                sentence_significance_dict = {}
                sentences = open(corpus_file).read().splitlines()
                for sentence in sentences:
                    if sentence:
                        sentence_significance_dict[sentence] = calc_significance_factor(sentence,
                                                                                        query[int(each_query)])

            sorted_dict = sorted(sentence_significance_dict.items(), key=operator.itemgetter(1), reverse=True)

            counter = 0
            snippet_lst = []
            flag = False
            for key, val in sorted_dict:
                if counter == 0 and val == 0.0:
                    flag = False
                    break
                if counter < 3:
                    snippet_lst.append(key)
                    counter += 1
                    flag = True
            if flag:
                write_to_file(f, corpus_file, snippet_lst, query[int(each_query)])  # Calling function to write in file


# Function to write data in file
def write_to_file(f, corpus_file, snippet_list, query):
    line = ""
    for snippet in snippet_list:
        for term in snippet.split(" "):
            if term.lower() in query.split(" ") and term.lower() not in stopwords:
                line += "<b> " + term + " </b>" + " "
            else:
                line += term + " "
        line += "...\n"
    f.write("Snippet for file " + corpus_file + " : \n")
    f.write(line + "\n")


# Main function
if __name__ == '__main__':
    query_dict = QueryRead.read_query_file()
    for each in query_dict:
        temp = ""
        i = 0
        for item in query_dict[each]:
            if i == 0:
                temp += item
            else:
                temp += " " + item
            i += 1
        query_dict[each] = temp

    with open("Bonus_tasks_Output/Snippets.txt", 'w') as f:
        generate_snippet(f, query_dict)
        f.close()
