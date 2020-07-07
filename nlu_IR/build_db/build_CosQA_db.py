import os, sys
from tqdm import tqdm
from .. import config
from ..std import *
import logging

logger = logging.getLogger(__name__)
import sqlite3
from . import io_CosQA


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
	                    help='Command: {build_all} for building CosQA database. {test_build} for testing building db.'
	                         '{test_db} for testing database.')
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
	
	if args.cmd == 'build_all':
		build_all(args.doc_path)
	
	elif args.cmd == 'test_build':
		test_build()
	
	elif args.cmd == 'test_db':
		test_db()
	
	else:
		raise ValueError('Command {} not defined!'.format(args.cmd))


def test_build():
	test_file = './data/cosQA/doc/wiki-entities_qa_tag_to_movie_dev_doc.json'
	
	# make db-storing directory and test whether db exits
	test_dir = config.DATABASE_ROOT / "test_SSQA_db"
	new_dir(test_dir, clear=True)
	
	conn = sqlite3.connect(str(test_dir / 'test.db'))
	c = conn.cursor()
	c.execute("CREATE TABLE documents (did PRIMARY KEY, title_en text, title_zh text, "
	          "url text, content_en text, content_zh text);")
	
	# Read lesson from json files
	logger.info("Start inserting into database...")
	num_doc = 0
	for structure_tuple in tqdm(io_CosQA.json2st(test_file)):
		num_doc += 1
		_insert_one(c, structure_tuple)
	
	logger.info("Inserted {} documents.".format(num_doc))
	logger.info("Committing...")
	conn.commit()
	conn.close()
	logger.info("Complete!")


def test_db():
	# instantiate SSQA_DB
	test_db_fp = config.DATABASE_ROOT / "test_SSQA_db" / "test.db"
	myDB = CosQA_DB(test_db_fp)
	qids = myDB.get_dids()
	lprint("qids: {}".format(qids))
	
	test_qid = qids[0]
	lprint("{} lesson_str_en: {}".format(test_qid, myDB.get_content_zh(test_qid)))
	lprint("{} lesson_str_cn: {}".format(test_qid, myDB.get_content_en(test_qid)))
	
	# close database
	myDB.close()


def _insert_one(cursor, structure_tuple):
	cursor.execute("INSERT OR REPLACE INTO documents VALUES (?,?,?,?,?,?)", structure_tuple)


def build_all(doc_dir):
	# make db-storing directory and test whether db exits
	new_dir(config.DATABASE_ROOT, clear=False)
	if os.path.isfile(config.DB_COSQA):
		raise RuntimeError('The database already exists!')
	
	conn = sqlite3.connect(str(config.DB_COSQA))
	c = conn.cursor()
	c.execute("CREATE TABLE documents (did PRIMARY KEY, title_en text, title_zh text, "
	          "url text, content_en text, content_zh text);")
	
	# Read lesson from json files
	logger.info("Start inserting into database...")
	num_doc = 0
	for fp in list_fps(doc_dir):
		for structure_tuple in tqdm(io_CosQA.json2st(fp)):
			num_doc += 1
			_insert_one(c, structure_tuple)
	
	logger.info("Inserted {} documents.".format(num_doc))
	logger.info("Committing...")
	conn.commit()
	conn.close()
	logger.info("Complete!")


class CosQA_DB:
	def __init__(self, db_path=config.DB_COSQA):
		self.conn = sqlite3.connect(str(db_path))
	
	def __enter__(self):
		return self
	
	def __exit__(self, *args):
		self.close()
	
	def close(self):
		self.conn.close()
	
	def get_dids(self):
		cursor = self.conn.cursor()
		cursor.execute("SELECT did FROM documents")
		results = [r[0] for r in cursor.fetchall()]
		cursor.close()
		return results
	
	def get_title_zh(self, qid):
		cursor = self.conn.cursor()
		cursor.execute("SELECT title_zh FROM documents WHERE did = ?",
		               (qid,))
		result = cursor.fetchone()[0]
		cursor.close()
		return result
	
	def get_title_en(self, qid):
		cursor = self.conn.cursor()
		cursor.execute("SELECT title_en FROM documents WHERE did = ?",
		               (qid,))
		result = cursor.fetchone()[0]
		cursor.close()
		return result
	
	def get_content_zh(self, qid):
		cursor = self.conn.cursor()
		cursor.execute("SELECT content_zh FROM documents WHERE did = ?",
		               (qid,))
		result = cursor.fetchone()[0]
		cursor.close()
		return result
	
	def get_content_en(self, qid):
		cursor = self.conn.cursor()
		cursor.execute("SELECT content_en FROM documents WHERE did = ?",
		               (qid,))
		result = cursor.fetchone()[0]
		cursor.close()
		return result


if __name__ == '__main__':
	main()
