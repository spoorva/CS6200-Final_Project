import re
import pdb
import sys
import traceback

import corpusGeneration
import nltk

index = {}
inverted_index = {}


def main(*args, **kw):

    with open("C:\\Users\\Poorva\\Downloads\\test-collection\\cacm_stem.txt", "r") as file:

        j = 0
        text =""
        lines = file.readlines()
        for i in range(0, len(lines)):

            line = lines[i]

            if line[0] == "#":

                j = i + 1

                docid = line[2:]



                while "#" not in lines[j] :

                        text = text + lines[j]
                        j = j + 1


                        if (j >= len(lines)):
                           break;



                match = re.search(r'\sam|\spm', text)

                if match:

                        index[int(docid.strip())] = text[:match.end() -2].split()

                text = ""



main()

for key, value in index.items():
    for v in value:
        inverted_index.setdefault(v, []).append(key)

for k, v in inverted_index.items():
    print(k, ":", v)

