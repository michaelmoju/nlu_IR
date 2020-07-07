import re
from ..std import *
from .Const import sep_bar1, sep_bar2
from . import util as Util

logger = logging.getLogger(__name__)


# json to structure
def json2st(fp):
	"""
	input: fp, e.g., '/data/cosQA/doc/wiki-entities_qa_tag_to_movie_dev_doc.json'
	"""
	documents = json_load(fp)
	for doc in documents:
		DID_URL_RGX = re.compile(r'https://www.wikidata.org/wiki/(Q.*)')
		
		title_en = doc['title']['en']
		assert title_en
		title_zh = doc['title']['zh'] if not None else ""
		
		url = doc['ref']['en']['url'] if not None else ""
		
		if not doc['ref']['en']['wikidata_url']:
			continue
		
		did = DID_URL_RGX.findall(doc['ref']['en']['wikidata_url'])[0]
		
		content_en = doc['summary']['en'] if not None else ""
		content_zh = doc['summary']['zh'] if not None else ""
		
		yield did, title_en, title_zh, url, content_en, content_zh