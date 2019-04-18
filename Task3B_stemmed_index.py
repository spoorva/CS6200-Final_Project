import re

import corpusGeneration
import nltk

index = {}

with open("C:\\Users\\Poorva\\Downloads\\test-collection\\cacm_stem.txt", "r") as file:

    j = 0
    text =""
    lines = file.readlines()
    for i in range(0, len(lines)):

        line = lines[i]

        if line[0] == "#":

            j = i + 1

            docid = line[2:]
            print("DOCID : ", docid)

            while "#" not in lines[j]:

                text = text + lines[j]
                j = j + 1


            match = re.search(r'\sam|\spm', text)

            if match:
                print(text[:match.end() -2 ])

            text = ""




