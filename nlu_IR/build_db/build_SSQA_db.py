import os, sys
from tqdm import tqdm
from .. import config
from ..std import *
import logging
logger = logging.getLogger(__name__)
import sqlite3
from . import io_SSQA


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
	                    help='Command: {build_all} for building SSQA database. {test_build} for testing building db.'
	                         '{test_db} for testing database.')
	parser.add_argument('-xml_path',
	                    default=config.DS_SSQA,
	                    help='/path/to/SSQA/Elementary_Social_Studies_v2.9')
	
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
		build_all(args.xml_path)
	
	elif args.cmd == 'test_build':
		test_build()
		
	elif args.cmd == 'test_db':
		test_db()
	
	else:
		raise ValueError('Command {} not defined!'.format(args.cmd))


def test_build():
	test_file = './data/SSQA/Elementary_Social_Studies_v2.9/Develop/PubB-G6a-0302.xml'
	
	# make db-storing directory and test whether db exits
	test_dir = config.DATABASE_ROOT / "test_SSQA_db"
	new_dir(test_dir, clear=True)
	
	conn = sqlite3.connect(str(test_dir / 'test.db'))
	c = conn.cursor()
	c.execute("CREATE TABLE lessons (Lid PRIMARY KEY, lesson_str text);")
	
	# Read lesson from xml files
	lessons = dict()
	Lid, _, lesson_str, _ = io_SSQA.xml2st(test_file, clean_title=True)
	assert Lid not in lessons, "{} duplicated!".format(Lid)
	lessons[Lid] = lesson_str
	logger.info("Read {} lessons from xml files.".format(len(lessons)))
	
	# insert into database
	logger.info("Start inserting into database...")
	for Lid, lesson_str in tqdm(lessons.items()):
		_insert_one(c, Lid, lesson_str)
	
	logger.info("Inserted {} lessons.".format(len(lessons)))
	logger.info("Committing...")
	conn.commit()
	conn.close()
	logger.info("Complete!")
	
	
def test_db():
	# instantiate SSQA_DB
	test_db_fp = config.DATABASE_ROOT / "test_SSQA_db" / "test.db"
	myDB = SSQA_DB(test_db_fp)
	Lids = myDB.get_Lids()
	lprint("Lids: {}".format(Lids))
	
	test_Lid = Lids[0]
	lprint("{} lesson_str: {}".format(test_Lid, myDB.get_lesson_str(test_Lid)))
	
	# close database
	myDB.close()
	
	
def _insert_one(cursor, Lid, lesson_str):
	cursor.execute("INSERT OR REPLACE INTO lessons VALUES (?,?)", (Lid, lesson_str))
	

def build_all(xml_dir):
	# make db-storing directory and test whether db exits
	new_dir(config.DATABASE_ROOT, clear=False)
	if os.path.isfile(config.DB_SSQA):
		raise RuntimeError('The database already exists!')
		
	conn = sqlite3.connect(str(config.DB_SSQA))
	c = conn.cursor()
	c.execute("CREATE TABLE lessons (Lid PRIMARY KEY, lesson_str text);")
	
	# Read lesson from xml files
	lessons = dict()
	sets = ['Train', 'Develop', 'Test']
	for set in sets:
		set_dir = str(xml_dir) + '/{}'.format(set)
		
		logger.info("Read {} set".format(set))
		for fp in tqdm(list_fps(set_dir, ext="xml")):
			Lid, _, lesson_str, _ = io_SSQA.xml2st(fp, clean_title=True)
			assert Lid not in lessons, "{} duplicated!".format(Lid)
			lessons[Lid] = lesson_str
	logger.info("Read {} lessons from xml files.".format(len(lessons)))
	
	# insert into database
	logger.info("Start inserting into database...")
	for Lid, lesson_str in tqdm(lessons.items()):
		_insert_one(c, Lid, lesson_str)
	
	logger.info("Inserted {} lessons.".format(len(lessons)))
	logger.info("Committing...")
	conn.commit()
	conn.close()
	logger.info("Complete!")
	
	
class SSQA_DB:
	def __init__(self, db_path=config.DB_SSQA):
		self.conn = sqlite3.connect(str(db_path))
	
	def __enter__(self):
		return self
	
	def __exit__(self, *args):
		self.close()
		
	def close(self):
		self.conn.close()
		
	def get_Lids(self):
		cursor = self.conn.cursor()
		cursor.execute("SELECT Lid FROM lessons")
		results = [r[0] for r in cursor.fetchall()]
		cursor.close()
		return results
	
	def get_lesson_str(self, Lid):
		cursor = self.conn.cursor()
		cursor.execute("SELECT lesson_str FROM lessons WHERE Lid = ?",
		               (Lid,))
		result = cursor.fetchone()[0]
		cursor.close()
		return result
	
	
if __name__=='__main__':
	main()