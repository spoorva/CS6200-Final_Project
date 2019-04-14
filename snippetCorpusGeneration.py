from bs4 import BeautifulSoup
import os
import glob
import traceback
import re

# Defining global variables
directory = 'Snippet_Corpus'


# Function to read articles of cacm HTML files and generate corpus from them
def get_content():
    try:
        count = 1
        path = 'cacm'
        for filename in glob.glob(os.path.join(path, '*.html')):
            with file(filename) as f:
                article_name = filename.strip('cacm/').strip('.html')
                content = f.read()
                count += 1

                soup = BeautifulSoup(content, 'html.parser')
                soup.prettify().encode('utf-8')

                pre_text = soup.find('pre').get_text().encode('utf-8')

                content_text = pre_text
                processed_text = text_transformation(content_text)
                write_to_file(processed_text, article_name)
                f.close()
    except:
        print ('Error in try block of fetch_content!')
        print (traceback.format_exc())


# Function to perform text transformation on the string provided to it as argument
def text_transformation(content):
    list_of_lines = []
    for lines in content.splitlines():
        new_lines = re.sub(r'[@_!\s^&*?#=+$~%:;\\/|<>(){}[\]"\']', ' ', lines)
        content_word_list = []
        for word in new_lines.split():
            word_length = len(word)
            if word[word_length - 1:word_length] == '-' \
                    or word[word_length - 1:word_length] == ',' \
                    or word[word_length - 1:word_length] == '.':
                word = word[:word_length - 1]
                content_word_list.append(remove_punctuation(word))
            else:
                content_word_list.append(remove_punctuation(word))
        content_word_list = [x for x in content_word_list if x != '']
        content_word_list = " ".join(content_word_list)
        list_of_lines.append(content_word_list)
        if ' PM ' in content_word_list or 'PM' in content_word_list or 'PMB ' in content_word_list:
            break
        elif ' AM ' in content_word_list or 'AM ' in content_word_list or ' AM' in content_word_list:
            break
    return list_of_lines


# Function to remove irrelevant punctuations before a word
def remove_punctuation(word):
    while word[:1] == "-" or word[:1] == "," or word[:1] == ".":
        if re.match(r'^[\-]?[0-9]*\.?[0-9]+$', word):
            return word
        if word[:1] == "-" or word[:1] == "." or word[:1] == ",":
            word = word[1:]
        else:
            return word
    return word


# Function to write the content in file
def write_to_file(content, file_name):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_index_terms = open(directory + '/' + file_name + '.txt', 'w')
        for items in content:
            file_index_terms.write(items + "\n")
        file_index_terms.close()
    except:
        print("Error in try block of write_to_file!", traceback.format_exc())
