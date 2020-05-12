import json
import unicodedata
import re
from urllib.parse import unquote

EDGE_XY = re.compile(r'<a href="(.*?)">(.*?)</a>')


def load_jsonl(fin):
	d_list = []
	for line in fin:
		d_list.append(json.loads(line))
	return d_list


def NFD_normalize(text):
	text = unicodedata.normalize('NFD', text)
	return text[0].capitalize() + text[1:]


def get_hyperlinks(sentence):
	"""
	x, y in ret
	x: the linked wikipedia page title
	y: the text in the sentence
	e.g.,
	[('Pam%20Beesly', 'Pam'), ('Michael%20Scott%20%28The%20Office%29', 'Michael')]
	"""
	ret = EDGE_XY.findall(sentence)
	return [(unquote(x), y) for x, y in ret]
