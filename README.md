# CS6200-Final_Project
## Search Engine Implementation

Members - <br>
Nanditha Sundararajan <br>
Poorva Sonparote<br>
Shruti Parpattedar

<br>

Language used - Python and Java <br>
Coded in version - Python 3.7.2

### Setup
This code requires the following software packages installed for it to run successfully:
<li> Python 3.7 <br>
	Download and install from "https://www.python.org/downloads/"<br>
<li> Lucene 4.7.2 <br>
	Download and install Lucene from<br>
	https://lucene.apache.org/ <br>
	https://archive.apache.org/dist/lucene/java/4.7.2/
<li> BeautifulSoup package <br>
	Can be downloaded from "https://www.crummy.com/software/BeautifulSoup/" <br>
	Can be installed using pip, by entering the following command in Terminal or Command Line :

		 pip install beautifulsoup4

### Compile and Run
Unzip the given solution folder into a local directory. All necessary files required to run 
this project will be extracted.


### Phase 1 - 
<b>Task 1 - Four baseline runs </b><br>
Implementation of TFIDF, Query Likelihood Model (JM smoothed) and BM25 using python. The program internally 
call Indexer.py and Parser.py to parse and index the corpus.

Implementation of Lucene’s default retrieval model using Java. The helper program Query_cleaning.py cleans 
the queries so that they can be used by Lucene.

Run the following commands - <br>
    Task1-First3Runs.py <br>
    Query_cleaning.py <br>
    Lucene-proj/src/LuceneRun.java<br><br>
    
<b>Task 2 - Query Enhancement<br></b>
Implementation of two query enhancement techniques - query time stemming and pseudo relevance with BM25 retrieval
model. The program internally call Indexer.py and Parser.py to parse and index the corpus.

Run the following commands - <br>
Task2-QueryTimeStemming.py <br>
Task2-PseudoRelevance.py<br><br>

<b>Task 3 - Stopping and Stemming Index<br></b>
Implementation of stopped corpus with no stemming and stemmed corpus with stemmed queries with BM25 and IFIDF
retrieval models. The program internally call Indexer.py and Parser.py to parse and index the corpus.

Run the following commands - <br>
Task3-StoppedIndex.py<br>
Task3-StemmedIndex.py<br><br>

### Phase 2 - 
Implementation of snippet generation and query highlighting. The program internally call Indexer.py and 
Parser.py to parse and index the corpus, and snippetGeneration.py for snippet generation.

Run the following commands - <br>
Phase2Run.py <br><br>

### Phase 3 - 
<b>Ninth run - Query Expansion using Pseudo Relevance Feedback with Stopping </b><br>
Implementing query enhancement using pseudo relevance feedback and stopping. The program internally 
call Indexer.py and Parser.py to parse and index the corpus.

Run the following command - <br>
Phase3Run.py <br><br>

<b> Evaluation </b><br>
Evaluating the various runs based on MAP, MRR, Precision, Recall, Precision @5 and @20 and Recall @5 and @20. <br>
Reads the list of runs to be evaluated from a file named Output_files_list.txt.

Run the following command - <br>
Evaluation.py<br><br>

### Extra Credit - 
Implementation of a search engine based on the Relevance Model using pseudo-relevance feedback and
KL-Divergence for scoring. The program internally call Indexer.py and Parser.py to parse and index 
the corpus.

Run the following command - <br>
KL_Divergence.py<br>


<b><i> All the outputs are stored in the Outputs Folder and all the evaluation results, along with
 the compiled evaluations and MAP-MRR summary are stored in Evaluation folder.<b><i>



    


