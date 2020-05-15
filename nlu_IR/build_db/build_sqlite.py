import bz2
import json
import sqlite3
from tqdm import tqdm
from ..std import *
from .. import config
from .db_utils import NFD_normalize, get_hyperlinks

logger = logging.getLogger(__name__)


def process_wiki_bz2(bz2_fp):
	""" Process enwiki-20171001-pages-meta-current-withlinks-abstracts

	dict_keys(['id', 'url', 'title', 'text', 'charoffset', 'text_with_links', 'charoffset_with_links'])
	"""
	
	with bz2.open(bz2_fp, 'rb') as fin:
		extracted_docs = []
		for line in fin:
			article = json.loads(line)
			plain_text = "\t".join(article['text'])  # sentences are split by "\t"
			org_title = article['title']
			nrm_title = NFD_normalize(org_title)
			if org_title != nrm_title:
				log_debug("org_title:{}, nrm_title:{}".format(org_title, nrm_title), logger)
			
			text_with_links = "\t".join(article['text_with_links'])
			hyper_link_titles = [ret[0] for ret in get_hyperlinks(text_with_links)]
			hyper_link_titles = '***'.join(hyper_link_titles)
			extracted_docs.append((article['id'], article['url'], plain_text, hyper_link_titles, org_title))
	return extracted_docs


def build_db(wiki_dir, save_path, num_workers=None):
	"""Store a wikipedia corpus in sqlite.
	"""
	if os.path.isfile(save_path):
		raise RuntimeError('%s already exists!' % save_path)
	
	wiki_files = [f for f in wiki_dir.glob("*/wiki_*.bz2")]
	logger.info("Read %d wikifiles." % len(wiki_files))
	
	conn = sqlite3.connect(config.DB_HOTPOT_WIKI)
	c = conn.cursor()
	c.execute("CREATE TABLE documents (id PRIMARY KEY, url text, text text, hyper_link_titles text, org_title text);")
	
	doc_num = 0
	for wiki_file in tqdm(wiki_files):
		extracted_docs = process_wiki_bz2(wiki_file)
		doc_num += len(extracted_docs)
		c.executemany("INSERT OR REPLACE INTO documents VALUES (?,?,?,?,?)", extracted_docs)
	
	logger.info("Read %d documents." % doc_num)
	logger.info("Commit to database.")
	conn.commit()
	conn.close()


def main():
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('-llv',
	                    default='INFO',
	                    help='Logging level')
	parser.add_argument('-log',
	                    default=None,
	                    help='Output log file')
	parser.add_argument('-wiki_dir',
	                    default=config.HOTPOT_WIKI_ABS,
	                    help='/path/to/wiki_files')
	parser.add_argument('-save_path',
	                    default=config.DB_HOTPOT_WIKI,
	                    help='/path/to/save/db.db')
	parser.add_argument('-num_workers',
	                    default=None,
	                    help='Number of CPU processes (for tokenizing, etc)')
	
	args = parser.parse_args()
	
	myLogFormat = '%(asctime)s ***%(levelname)s*** [%(name)s:%(lineno)s] - %(message)s'
	logging.basicConfig(level=str2llv(args.llv), format=myLogFormat, datefmt='%Y/%m/%d %H:%M:%S')
	if args.log:
		myhandlers = log_w(args.log)
		logger.addHandler(myhandlers)
		logger.log(100, ' '.join(sys.argv))
	else:
		logger.log(100, ' '.join(sys.argv))
	
	build_db(args.wiki_dir, args.save_path, args.num_workers)


if __name__ == '__main__':
	main()
