# Lucene search
Searcher for multiple corpora and projects in NLU_lab

Searchers:  
- <a href="#1-cosqa-searcher"> 1. CosQA searcher </a> 
- <a href="#2-ssqa-searcherr"> 2. SSQA searcher </a>>
- 3\. HotpotQA searcher

## 1. CosQA searcher
### Indexing
First, you should index all the documents to be searched. This only needs to be run once.  
In the project file, run:
```bash
python -m nlu_IR.lucene_search.cosQA_search -cmd index_all -doc_path /path/to/cosQA/doc/
```
change `/path/to/cosQA/doc/` to the path of the document json files.  
This will create two directories in `database` which are English and Chinese indexed directories.  
Once you've created the indexed directories successfully, the searcher can search from here in the future.

### Test search
Run the test function to search by a query. Run:
```bash
python -m nlu_IR.lucene_search.cosQA_search -cmd test_search
```
The output should be:
```
[('Q3536311', 'Tracker (2011 film)', 'Tracker is a ...', 9.377347946166992)]
```

To directly use the searcher API, please refer to the `test_search` function in [cosQA_search.py](cosQA_search.py)

## 2. SSQA searcher