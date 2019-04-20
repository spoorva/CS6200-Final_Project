from xml.etree import cElementTree as et
import re
import pickle
import os



q_dict = {}
# import the query file
q_file = 'test-collection/cacm.query.txt'
q_content = open(q_file, 'r').read()

# Convert it into an XML format for cleaning
q_content = "<ROOT>\n" + q_content + "\n</ROOT>"
q_content = q_content.replace("</DOCNO>", "</DOCNO>\n<QUERY>")
xml_content_string = q_content.replace("</DOC>", "</QUERY>\n</DOC>")


path_r = et.fromstring(xml_content_string)



for query in path_r:
    query_id = query.find('DOCNO').text.strip()
    quer = query.find('QUERY').text
    quer = quer.lower().replace("\n", " ")
    quer= re.sub(' +', ' ', quer).strip()
    quer = re.sub(r"[^0-9A-Za-z,-\.:\\$]", " ", quer)          
    quer = re.sub(r"(?!\d)[$,%,:.,-](?!\d)", " ", quer, 0)     
    quer = quer.split()
    for l in quer:
        if l.startswith('-'):
            l.replace(l, l.split('-')[1])
        if l.endswith('-'):
            l.replace(l, l.split('-')[0])
        else:
            continue
    quer = ' '.join(quer)
    q_dict[query_id] = quer


for key, value in q_dict.items():
    print("Query after cleaning " + key + " : " + value)


# write the output to the file
file = open("cleaned_query.txt", 'w', encoding='utf-8')
for qid in q_dict:
    file.write(qid + "\t" + q_dict[qid] + "\n")
file.close()

print("DONE")