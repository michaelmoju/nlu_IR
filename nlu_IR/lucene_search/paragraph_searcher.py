import lucene
from org.apache.lucene.analysis.cn.smart import SmartChineseAnalyzer
from org.apache.lucene.store import RAMDirectory
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
from org.apache.lucene.document import Document, StringField, TextField, Field

mySimilarity = ClassicSimilarity

class ChineseRamIndexer:
	def __init__(self):
		lucene.initVM()
		indexDir = RAMDirectory()
		analyzer = SmartChineseAnalyzer()
		writerConfig = IndexWriterConfig(analyzer)
		writerConfig.setOpenMode(
			IndexWriterConfig.OpenMode.CREATE)  # create new directory, remove previously indexed documents
		writerConfig.setSimilarity(mySimilarity())
		self.indexDir = indexDir
		self.writer = IndexWriter(indexDir, writerConfig)
	
	def add(self, pid, ptext):
		doc = Document()
		doc.add(StringField("pid", pid, Field.Store.YES))
		doc.add(TextField("ptext", ptext, Field.Store.YES))
		self.writer.addDocument(doc)
	
	def close(self):
		self.writer.close()


class ParagSearcher:
	def __init__(self, indexDir):
		lucene.initVM()
		analyzer = SmartChineseAnalyzer()
		self.reader = DirectoryReader.open(indexDir)
		self.searcher = IndexSearcher(self.reader)
		self.searcher.setSimilarity(mySimilarity())
		self.analyzer = analyzer
		logger.info('search similarity:{}'.format(self.searcher.getSimilarity()))
	
	def search(self, query_text, top_n=1):
		query_text = query_text.strip()
		#         query = QueryParser("ptext", self.analyzer).parse(QueryParser.escape(query_text.strip()))
		query = QueryParser("ptext", self.analyzer).parse(query_text)
		scoreDocs = self.searcher.search(query, top_n).scoreDocs
		
		print(scoreDocs)
		for scoreDoc in scoreDocs:
			docIndex = scoreDoc.doc
			doc = self.searcher.doc(docIndex)
			print(doc['pid'])
			print(self.searcher.explain(query, docIndex))
	
	def close(self):
		self.reader.close()


if __name__ == '__main__':

	
	