from wiki_util import wiki_db_tool
from . import config
from sqlitedict import SqliteDict
import json
from tqdm import tqdm
from inspect_wikidump.inspect_whole_file import get_first_paragraph_index
from utils import common

import lucene
from java.nio.file import Paths
from java.io import File
from org.apache.pylucene.analysis import PythonAnalyzer
from org.apache.lucene.analysis import LowerCaseFilter, StopFilter
from org.apache.lucene.analysis.core import StopAnalyzer
from org.apache.lucene.analysis.en import PorterStemFilter, EnglishAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer, StandardTokenizer
from org.apache.lucene.document import Document, Field, StringField, TextField, StoredField
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, IndexReader, DirectoryReader
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.search.similarities import ClassicSimilarity, BM25Similarity

from .std import lprint
import logging
logger = logging.getLogger(__name__)


class PorterStemmerAnalyzer(PythonAnalyzer):

	def createComponents(self, fieldName):
		source = StandardTokenizer()
		filter1 = LowerCaseFilter(source)
		filter1 = PorterStemFilter(filter1)
		filter1 = StopFilter(filter1, EnglishAnalyzer.ENGLISH_STOP_WORDS_SET)

		return self.TokenStreamComponents(source, filter1)

	def initReader(self, fieldName, reader):
		return reader


def lucene_indexing():
	lucene.initVM()
	whole_tokenized_db_cursor = wiki_db_tool.get_cursor(config.WHOLE_PROCESS_FOR_RINDEX_DB)
	whole_tokenized_db_cursor.execute("SELECT * from unnamed")

	indexDir = SimpleFSDirectory(Paths.get(str(config.LUCENE_INDEXED)))
	analyzer = PorterStemmerAnalyzer()
	writerConfig = IndexWriterConfig(analyzer)
	writer = IndexWriter(indexDir, writerConfig)

	lprint("Building lucene index ...")
	with SqliteDict(str(config.WHOLE_WIKI_DB), flag='r', encode=json.dumps, decode=json.loads) as whole_wiki_db:
		for key, value in tqdm(whole_tokenized_db_cursor, total=config.TOTAL_ARTICLE_NUMBER_WHOLE):

			item = json.loads(value)
			article_title = item['title']
			article_clean_text = item['clean_text']
			article_poss = item['poss']

			# TODO: change it to extract abstract wiki?
			# get the first paragraph which has the length >= 50? so weired.
			abs_index = get_first_paragraph_index(whole_wiki_db[article_title])

			if abs_index == -1:  # document too short
				valid_page = False

			# only title
			title_term_list = []
			title_poss_list = []

			# only abstract content
			abstract_term_list = []
			abstract_poss_list = []

			assert len(article_clean_text) == len(article_poss)

			for p_i, (paragraph_text, paragraph_poss) in enumerate(zip(article_clean_text, article_poss)):
				for sent_text, sent_poss in zip(paragraph_text, paragraph_poss):
					if p_i == 0:  # In title.
						title_term_list.extend(sent_text)
						title_poss_list.extend(sent_poss)
						continue  # If the terms are in title, we don't include those terms in abstract and article term.
					else:
						if p_i == abs_index:  # If the terms are in abstract
							abstract_term_list.extend(sent_text)
							abstract_poss_list.extend(sent_poss)

			added_title = article_title
			added_text = " ".join(title_term_list + abstract_term_list)

			doc = Document()
			doc.add(Field("title", added_title, StoredField.TYPE))
			doc.add(Field("text", added_text, TextField.TYPE_STORED))
			writer.addDocument(doc)
	writer.close()


def lucene_retri_doc(query_text, top_k=50):
	lucene.initVM()
	analyzer = PorterStemmerAnalyzer()
	indexDir = SimpleFSDirectory(Paths.get(str(config.LUCENE_INDEXED)))
	open_dir = DirectoryReader.open(indexDir)  
	searcher = IndexSearcher(open_dir)

	query = QueryParser("text", analyzer).parse(QueryParser.escape(query_text.strip()[:-1]))
	scoreDocs = searcher.search(query, top_k).scoreDocs

	doc_list = []
	for scoreDoc in scoreDocs:
		doc = searcher.doc(scoreDoc.doc)
		doc_list.append([scoreDoc.score, doc['title']])

	open_dir.close()
	return doc_list


def term_based_doc_retri(hotpot_set):
	fullwiki_list = common.load_json(hotpot_set)
	print("{} questions".format(len(fullwiki_list)))

	retri_list = []
	for item in tqdm(fullwiki_list):
		saved_tfidf_item = dict()
		question = item['question']
		qid = item['_id']

		doc_list = lucene_retri_doc(question, top_k=50)
		saved_tfidf_item['question'] = question
		saved_tfidf_item['qid'] = qid
		saved_tfidf_item['doc_list'] = doc_list

		retri_list.append(saved_tfidf_item)
	return retri_list


if __name__ == '__main__':
	lucene_indexing()

	print("retrieve train set ...")
	saved_items = term_based_doc_retri(config.TRAIN_FILE)
	common.save_jsonl(saved_items, config.TRAIN_TERM_BASED)

	print("retrieve dev set ...")
	saved_items = term_based_doc_retri(config.DEV_FULLWIKI_FILE)
	common.save_jsonl(saved_items, config.DEV_TERM_BASED)

	print("retrieve test set ...")
	saved_items = term_based_doc_retri(config.TEST_FULLWIKI_FILE)
	common.save_jsonl(saved_items, config.TEST_TERM_BASED)


