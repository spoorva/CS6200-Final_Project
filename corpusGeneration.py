from bs4 import BeautifulSoup
import os
import glob
import re
import traceback

# Defining global variables
all_files = []
directory = 'Corpus'


# Function to read articles of cacm html file and generate corpus from them
def get_content():
    try:
        count = 1
        path = 'cacm'
        for filename in glob.glob(os.path.join(path, '*.html')):
            with open(filename) as f:
                article_name = filename.strip('cacm/').strip('.html')
                content = f.read()
                count += 1

                soup = BeautifulSoup(content, 'html.parser')
                soup.prettify().encode('utf-8')

                pre_text = soup.find('pre').get_text().encode('utf-8')

                content_text = pre_text
                processed_text = text_transformation(content_text)
                processed_text = processed_text.lower()
                write_to_file(processed_text, article_name)
                f.close()
    except:
        print('Error in try block of fetch_content!', traceback.format_exc())


# Function to perform text transformation on the string provided to it as argument
def text_transformation(content):
    content = re.sub(r'[@_!\s^&*?#=+$~%:;\\/|<>(){}[\]"\']', ' ', content)
    content_word_list = []
    for word in content.split():
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

    # Removing noise from the text
    if ' PM ' in content_word_list or 'PM ' in content_word_list or 'PMB ' in content_word_list:
        content_word_list_proc = content_word_list.split('PM')[0]
        content_word_list_proc += " pm"
        return content_word_list_proc
    elif ' AM ' in content_word_list or 'AM ' in content_word_list:
        content_word_list_proc = content_word_list.split('AM')[0]
        content_word_list_proc += " am"
        return content_word_list_proc
    else:
        return content_word_list


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
        file_index_terms.write(content)
        file_index_terms.close()
    except:
        print("Error in try block of write_to_file!", traceback.format_exc())
