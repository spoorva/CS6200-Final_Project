from bs4 import BeautifulSoup
import io
# import requests
import re
import glob, os
import string

CURRENT_DIR = os.getcwd()
CORPUS_PATH = os.path.join(CURRENT_DIR, "cacm")
DOC_TOKENS_MAP = {}
TOKENIZED_CORPUS_PATH = os.path.join("TokenizedFile")
ps = string.punctuation
trans = str.maketrans(ps, "                                ")


def Tokenizer(filename):
    with io.open(filename, "r", encoding="utf-8") as file:
        lines = file.read()

    body_content = parse_html_doc(lines)

    # Tokenize using included function
    tokens = tokenize(body_content)

    # Using included function CASE FOLD
    tokens = case_fold(tokens)

    # Removing unnecessary punctuation
    tokens = punctuation_handler(tokens)

    # Saving tokens to file
    save_tokens_to_file(tokens, filename)


def parse_html_doc(raw_html):
    # Extracts main body content text from the raw html
    soup = BeautifulSoup(raw_html, 'html.parser')
    body = soup.find("pre").get_text()

    match = re.search(r'\sAM|\sPM', body)
    if match:
        body = body[:match.end()]

    return body


def tokenize(text_content):
    # Converts text into a list of tokens without spaces.
    raw_tokens = text_content.split()
    regex = re.compile('\w')

    return list(filter(regex.search, raw_tokens))


def case_fold(tokens):
    # Returns case-folded list of tokens.
    return [x.casefold() for x in tokens]


def punctuation_handler(tokens):
    punct_removed = []
    for token in tokens:
        punct_removed.append(token.translate(trans).strip())

    # Remove white-space tokens
    regex = re.compile('\S')
    return list(filter(regex.search, punct_removed))


def save_tokens_to_file(tokens, file):
    filename = os.path.basename(file)
    doc_id = filename[:-5]
    output_file = os.path.join(TOKENIZED_CORPUS_PATH, doc_id + ".txt")

    global DOC_TOKENS_MAP
    DOC_TOKENS_MAP[doc_id] = tokens
    with io.open(output_file, "w", encoding="utf-8") as tokenized_html:
        for token in tokens:
            tokenized_html.write(token + "\n")


def main():
    # Read input CACM raw documents corpus
    input_path = os.path.join(CORPUS_PATH, r"*.html")
    files = glob.glob(input_path)

    # Create output directory for tokenized files
    os.makedirs(TOKENIZED_CORPUS_PATH, exist_ok=True)

    for filename in files:
        Tokenizer(filename)

    print("Completed parsing documents.")

# main()
