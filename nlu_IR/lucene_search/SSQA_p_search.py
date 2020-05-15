from .. import config
from ..std import *
import logging

logger = logging.getLogger(__name__)

import lucene
from org.apache.lucene.analysis.cn.smart import SmartChineseAnalyzer
from org.apache.lucene.store import RAMDirectory
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, DirectoryReader
from org.apache.lucene.document import Document, StringField, TextField, Field
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.search.similarities import ClassicSimilarity, BM25Similarity
from org.apache.lucene.queryparser.classic import QueryParser
from ..build_db.build_SSQA_db import SSQA_DB
from ..build_db.io_SSQA import str_lesson2parags

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
	                    help='Command: {test_search} for searching')
	
	args = parser.parse_args()
	
	myLogFormat = '%(asctime)s ***%(levelname)s*** [%(name)s:%(lineno)s] - %(message)s'
	logging.basicConfig(level=str2llv(args.llv), format=myLogFormat, datefmt='%Y/%m/%d %H:%M:%S')
	if args.log:
		myhandlers = log_w(args.log)
		logger.addHandler(myhandlers)
		logger.log(100, ' '.join(sys.argv))
	else:
		logger.log(100, ' '.join(sys.argv))
	
	if args.cmd == 'test_search':
		test_search()
	
	else:
		raise ValueError('Command {} not defined!'.format(args.cmd))


def test_search():
	# query to be search
	test_query = '性別'
	
	# Specify a lesson and instantiate a searcher
	Lid = 'PubB-G6a-0302'
	test_db_fp = config.DATABASE_ROOT / "test_SSQA_db" / "test.db"
	mySearcher = ParagSearcher(Lid)
	
	"""
	search by calling searcher.search(query, top_n)
	return:
	A list of tuple(pid, content, score)
	"""
	
	ret_docs = mySearcher.search(query_text=test_query, top_n=1)
	print(ret_docs)
	
	# remember to close the searcher
	mySearcher.close()


class _ChineseRamIndexer:
	def __init__(self):
		indexDir = RAMDirectory()
		analyzer = SmartChineseAnalyzer()
		writerConfig = IndexWriterConfig(analyzer)
		
		# create new directory, remove previously indexed documents
		writerConfig.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
		writerConfig.setSimilarity(mySimilarity())
		logger.debug('search similarity:{}'.format(writerConfig.getSimilarity()))
		self.indexDir = indexDir
		self.writer = IndexWriter(indexDir, writerConfig)
	
	def add(self, pid, content):
		doc = Document()
		doc.add(StringField("pid", pid, Field.Store.YES))
		doc.add(TextField("content", content, Field.Store.YES))
		self.writer.addDocument(doc)
	
	def close(self):
		self.writer.close()
		
	def index_lesson(self, parags):
		for index, content in enumerate(parags):
			pid = 'p' + str(index)
			self.add(pid, content)
		self.close()
	

class ParagSearcher:
	def __init__(self, Lid, db_path=config.DB_SSQA):
		lucene.initVM()
		self.db = SSQA_DB(db_path)
		
		lesson_str = self.db.get_lesson_str(Lid)
		parags = str_lesson2parags(lesson_str)
		
		# Index a Lesson
		myIndexer = _ChineseRamIndexer()
		myIndexer.index_lesson(parags)
		myIndexer.close()

		self.reader = DirectoryReader.open(myIndexer.indexDir)
		self.searcher = IndexSearcher(self.reader)
		self.searcher.setSimilarity(mySimilarity())
		self.analyzer = SmartChineseAnalyzer()
		logger.debug('search similarity:{}'.format(self.searcher.getSimilarity()))
		
	def __exit__(self, *args):
		self.close()
	
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
			
			out_list.append((doc['pid'], doc['content'], scoreDoc.score))
		return out_list
	
	def close(self):
		self.db.close()
		self.reader.close()


if __name__ == '__main__':
	main()

