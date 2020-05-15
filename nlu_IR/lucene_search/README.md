# Lucene search
Searcher for multiple corpora and projects in NLU_lab.

Searchers:  
- <a href="#1-cosqa-searcher"> 1. CosQA searcher </a> 
- <a href="#2-ssqa-searcher"> 2. SSQA searcher </a>
- 3\. HotpotQA searcher

## 1. CosQA searcher
### Indexing
First, you should index all the documents to be searched. This only needs to be run once.  
In the project file, run:
```bash
python -m nlu_IR.lucene_search.cosQA_search -cmd index_all -doc_path /path/to/cosQA/doc/
```
change `/path/to/cosQA/doc/` to the path of the document json files.  
This will create 2 directories,which are English and Chinese indexed directories, in `nlu_IR/database`.  
Once you've created the indexed directories successfully, the searcher can search from here in the future.

### Test search
Run the test function to search by the testing query. Run:
```bash
python -m nlu_IR.lucene_search.cosQA_search -cmd test_search
```
The output should be:
```
[('Q3536311', 'Tracker (2011 film)', 'Tracker is a ...', 9.377347946166992)]
```

To directly use the searcher's API, please refer to the `test_search` function in [cosQA_search.py](cosQA_search.py)

## 2. SSQA searcher
### Paragraph search
To conduct paragraph search, you should input a lesson id and a query. 
The searcher will search from that lesson and return some paragraphs and the scores.
#### Build database
The first thing you should do is building the database that stores all lessons.  
In the project file, run:
```bash
python -m nlu_IR.build_db.build_SSQA_db -cmd build_all -xml_path /path/to/SSQA/Elementary_Social_Studies_v2.9
```

#### Test search
```bash
python -m nlu_IR.lucene_search.SSQA_p_search -cmd test_search
```
The output should be:
```
[('p20', '＊觀點小視窗：性別平等指每個人都應站在公平的立足點上發展潛能，不因生理、心理、社會及文化上的性別因素而受到限制。', 1.7605865001678467)]
```
To directly use the searcher's API, please refer to the `test_search` function in [SSQA_p_searcher.py](SSQA_p_search.py)