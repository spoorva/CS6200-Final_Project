import re
from collections import Set
from urllib.request import urlopen

from bs4 import BeautifulSoup
import requests

import corpusGeneration
import QueryRead
import json
import urllib

file = open(r"C:\Users\Poorva\Downloads\test-collection\cacm.query.txt")


def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError as e:
        return False
    return True

query = {}
count = 1
query_text = open(r"C:\Users\Poorva\Downloads\test-collection\cacm.query.txt")

new_queries_file = open("new_queries.txt", "w")

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



    #print("STOP WORDS -> ", QueryRead.stop_words())
    for i in QueryRead.stop_words():

        if i in query[count]:

            query[count].remove(i)

    str1 = "  ".join(str(e) for e in query[count])
    print(str1)

    headers = {"X-RapidAPI-Host": "wordsapiv1.p.rapidapi.com",
               "X-RapidAPI-Key": "3d91b5b661mshc5033075a07e3bap1c57bbjsnef1bff5d543d"}


    lst = []
    for term in query[count]:


        derivatives = set()
        lst.append(term)

        response = requests.get('https://wordsapiv1.p.mashape.com/words/' + term, headers=headers)

        if 'results' in response.json():
            for resp in (response.json().get('results')):

                if response.json().get('results') is not None and resp is not None and 'derivation' in resp:
                    for i in resp['derivation']:
                        derivatives.add(i)
        for j in derivatives:
                        lst.append(j)



        # print("Term -> ", term)
        #         print(("Possible derivatives -> ",  derivatives))


    str2 = " ".join(str(e) for e in lst)
    new_queries_file.write(str2)
    new_queries_file.write("\n")

    print(str2)
    count = count+1

