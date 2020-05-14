import re
from tqdm import tqdm
from .. import config
from ..std import *
import logging

logger = logging.getLogger(__name__)

import lucene
from java.nio.file import Paths
from org.apache.lucene.analysis.cn.smart import SmartChineseAnalyzer
from org.apache.lucene.analysis.en import EnglishAnalyzer
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, IndexReader, DirectoryReader
from org.apache.lucene.document import Document, StringField, TextField, Field
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.search.similarities import ClassicSimilarity, BM25Similarity
from org.apache.lucene.queryparser.classic import QueryParser

mySimilarity = BM25Similarity


def main():
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('-llv',
	                    default='INFO',
	                    help='Logging level')
	parser.add_argument('-log',
	                    default=None,
	                    help='Output log file')
	parser.add_argument('-cmd',
	                    required=True,
	                    help='Command: {index_all} for indexing the raw documents, {test_search} for searching')
	parser.add_argument('-doc_path',
	                    default=config.COS_WIKI,
	                    help='/path/to/cosQA/doc')
	
	args = parser.parse_args()
	
	myLogFormat = '%(asctime)s ***%(levelname)s*** [%(name)s:%(lineno)s] - %(message)s'
	logging.basicConfig(level=str2llv(args.llv), format=myLogFormat, datefmt='%Y/%m/%d %H:%M:%S')
	if args.log:
		myhandlers = log_w(args.log)
		logger.addHandler(myhandlers)
		logger.log(100, ' '.join(sys.argv))
	else:
		logger.log(100, ' '.join(sys.argv))
	
	if args.cmd == 'index_all':
		index_all(args.doc_path)
	
	elif args.cmd == 'test_search':
		test_search()


def test_search():
	# query to be search
	test_query = 'what movies did Temuera Morrison act in?'
	
	# instantiate a searcher, 'en' for English and 'zh' for Chinese
	mysearcher = CosQASearcher('en')
	
	"""
	search by calling searcher.search(query, top_n)
	return:
	A list of (did, title_en, content, score)
	"""
	
	ret_docs = mysearcher.search(query_text=test_query, top_n=1)
	print(ret_docs)
	
	# remember to close the searcher
	mysearcher.close()


class CosQAIndexer:
	def __init__(self, lang):
		lucene.initVM()
		
		if lang == 'zh':
			logger.info("index directory:{}".format(config.IDX_COS_ZH))
			indexDir = SimpleFSDirectory(Paths.get(str(config.IDX_COS_ZH)))
			analyzer = SmartChineseAnalyzer()
		elif lang == 'en':
			logger.info("index directory:{}".format(config.IDX_COS_EN))
			indexDir = SimpleFSDirectory(Paths.get(str(config.IDX_COS_EN)))
			analyzer = EnglishAnalyzer()
		else:
			raise ValueError('lang should be "zh" or "en", {} is invalid!'.format(lang))
		writerConfig = IndexWriterConfig(analyzer)
		writerConfig.setSimilarity(mySimilarity())
		logger.debug('writer similarity func: {}'.format(writerConfig.getSimilarity()))
		writer = IndexWriter(indexDir, writerConfig)
		self.writer = writer
	
	def add(self, did, title_en, content):
		doc = Document()
		doc.add(StringField("did", did, Field.Store.YES))
		doc.add(StringField("title_en", title_en, Field.Store.YES))
		doc.add(TextField("content", content, Field.Store.YES))
		self.writer.addDocument(doc)
	
	def close(self):
		self.writer.close()


class CosQASearcher:
	def __init__(self, lang):
		lucene.initVM()
		
		if lang == 'zh':
			indexDir = SimpleFSDirectory(Paths.get(str(config.IDX_COS_ZH)))
			analyzer = SmartChineseAnalyzer()
		elif lang == 'en':
			indexDir = SimpleFSDirectory(Paths.get(str(config.IDX_COS_EN)))
			analyzer = EnglishAnalyzer()
		else:
			raise ValueError('lang should be "zh" or "en", {} is invalid!'.format(lang))
		
		self.reader = DirectoryReader.open(indexDir)
		self.searcher = IndexSearcher(self.reader)
		self.searcher.setSimilarity(mySimilarity())
		self.analyzer = analyzer
		logger.debug('search similarity func: {}'.format(self.searcher.getSimilarity()))
	
	def search(self, query_text, top_n=1):
		query_text = query_text.strip()
		# query = QueryParser("content", self.analyzer).parse(QueryParser.escape(query_text.strip()))
		query = QueryParser("content", self.analyzer).parse(query_text)
		scoreDocs = self.searcher.search(query, top_n).scoreDocs
		
		out_list = []
		for scoreDoc in scoreDocs:
			docIndex = scoreDoc.doc
			doc = self.searcher.doc(docIndex)
			log_debug(doc, logger)
			log_debug(self.searcher.explain(query, docIndex), logger)
			
			out_list.append((doc['did'], doc['title_en'], doc['content'], scoreDoc.score))
		return out_list
	
	def close(self):
		self.reader.close()


def index_all(doc_path):
	def get_content(doc):
		DID_URL_RGX = re.compile(r'https://www.wikidata.org/wiki/(Q.*)')
		
		title_en = doc['title']['en']
		assert title_en
		url = doc['ref']['en']['url']
	
		if not doc['ref']['en']['wikidata_url']:
			return None
		
		did = DID_URL_RGX.findall(doc['ref']['en']['wikidata_url'])[0]
		
		content_en = doc['summary']['en']
		content_zh = doc['summary']['zh']
		
		if not content_en:
			return None
		if not content_zh:
			return None
		
		return did, title_en, url, content_en, content_zh
	
	raw_fps = list_fps(doc_path, 'json')
	logger.info("Read {} files".format(len(raw_fps)))
	
	# 	assert not os.path.exists(config.IDX_COS_EN), "{} already exists!".format(config.IDX_COS_EN)
	# 	assert not os.path.exists(config.IDX_COS_ZH), "{} already exists!".format(config.IDX_COS_ZH)
	
	new_dir(config.IDX_COS_EN)
	new_dir(config.IDX_COS_ZH)
	myIndexer_en = CosQAIndexer("en")
	myIndexer_zh = CosQAIndexer("zh")
	
	try:
		doc_num = 0
		logger.info("Start indexing...")
		for fp in tqdm(raw_fps):
			docs = json_load(fp)
			for doc in docs:
				if not get_content(doc):
					continue
				else:
					did, title_en, url, content_en, content_zh = get_content(doc)
				myIndexer_en.add(did, title_en, content_en)
				myIndexer_zh.add(did, title_en, content_zh)
				doc_num += 1
		logger.info("Indexed {} docs.".format(doc_num))
		myIndexer_en.close()
		myIndexer_zh.close()

	finally:
		myIndexer_en.close()
		myIndexer_zh.close()

if __name__ == '__main__':
	main()