import re
import xml.etree.ElementTree as ET

from ..std import *
from .Const import sep_bar1, sep_bar2
from . import util as Util

_PUNCT_SET = frozenset(["，", ",", "、", "；", "。", "：", "！", "!", "？", "?"])

logger = logging.getLogger(__name__)


def string_split(str):
	myOut = []
	mySeg = ''
	for iChar in str:
		mySeg += iChar
		if iChar in _PUNCT_SET:
			myOut.append(mySeg)
			mySeg = ''
	if mySeg:
		myOut.append(mySeg)
	return myOut


def _leaf2text(p):
	assert len(p) == 0
	myText = p.text.strip(' \t\r\n')
	insist(len(myText) > 0)
	insist(myText == p.text)
	insist(myText.find('\n') < 0)
	insist(myText.find('\r') < 0)
	insist(myText.find('\t') < 0)
	return myText


def _body2dat(p, dat, xpath=''):
	# for c in p: print(c.tag, c.attrib)
	myXpath = xpath
	if myXpath: myXpath += '/'
	myXpath += p.tag
	
	if len(p) == 0:
		# terminal
		dat.append((myXpath, _leaf2text(p)))
	else:
		# nonterminal
		for c in p: _body2dat(c, dat, myXpath)


def _qst2dat(qsts):
	def is_label(choice_txt, label_dict):
		for char in choice_txt:
			if char not in label_dict:
				return False
		return True
	
	q_dict = {'true-false': {}, 'multiple-choice': {}, 'multiple-select': {}}
	for q_i, q in enumerate(qsts):
		assert q.tag == 'QA'
		grade, qnum = re.search('IIS-MR-SOCIAL-GRADE(\d{2})-(\d{6})', q.attrib['ID']).groups()
		qid = grade + '-' + qnum
		qtype = q.attrib['Type']
		q_idx = q.attrib['idx']
		
		if qtype == 'true-false':
			q_text = q[0].text  # question
			a = q[1].text  # answer 對 or 錯
			assert qid not in q_dict['true-false'], "duplicate qid"
			q_dict['true-false'][qid] = (q_text, a)
		
		elif qtype == 'multiple-choice':
			q_text = q[0].text  # question
			choices = []
			if len(q) == 3:
				for choice in q[1]:  # ChoiceSet
					choice_id = choice.attrib['idx']
					choice_txt = choice.text
					choices.append(choice_id + ':' + choice_txt + '\n')
				a = int(q[2].attrib['idx']) - 1  # answer idx
			elif len(q) == 4:
				label_dict = {}
				for label in q[1]:  # ChoiceList
					label_dict[label.attrib['label']] = label.text
				for choice in q[2]:  # ChoiceSet
					choice_id = choice.attrib['idx']
					
					# choice
					if is_label(choice.text, label_dict):
						choice_txt = '|'.join([label_dict[label] for label in choice.text])
					else:
						choice_txt = choice.text
					choices.append(choice_id + ':' + choice_txt + '\n')
				a = int(q[3].attrib['idx']) - 1  # answer idx
			else:
				logger.error("multiple-choice has more element!")
			assert qid not in q_dict['multiple-choice'], "duplicate qid"
			q_dict['multiple-choice'][qid] = (q_text, choices, a)
		
		elif qtype == 'multiple-select':
			q_text = q[0].text  # question
			choices = [c.text for c in q[1]]  # choice set
			a = [int(a.attrib['idx']) - 1 for a in q[2]]  # answer idx list
			assert qid not in q_dict['multiple-select'], "duplicate qid"
			q_dict['multiple-select'][qid] = (q_text, choices, a)
	
	return q_dict


# xml to structure
def xml2st(fp, clean_title=True):
	"""
	input: fp, e.g., './data/SSQA/Elementary_Social_Studies_v2.9/Develop/PubB-G6a-0302.xml'
	return:
	# myFid: The lesson id, e.g.,
	# out_parags: A list of paragraphs that store a list of sentence(sid, text, start, end).
	# myLessonTxt: A string of the lesson context, use ||| to separate paragraph and || to separate sentence,
	             e.g., "p0-s0||p0-s1|||p1-s0|||p2-s0||p2-s1||p2-s2"
	q_dict: The dict which has keys ['true-false', 'multiple-choice', 'multiple-select']. Each value is a list of
			questions.
	"""
	myFid, myGrad = re.search('/(Pub.-G(\d)[ab]-\d{4})\.', str(fp)).groups()
	logger.debug(myFid)
	
	tree = ET.parse(fp)
	p = tree.getroot()
	for i in ['Machine-Reading-Corpus-File', 'Content', 'Unit']:
		assert p.tag == i
		if i != 'Unit':
			assert len(p) == 1
			p = p[0]
	assert len(p) == 2  # Body, QAset
	
	# read the lessons
	myBodyDat = []
	assert p[0].tag == 'Body'
	_body2dat(p[0], myBodyDat)
	logger.debug(myBodyDat)
	
	myLessonTxt = ""
	s_start = 0
	
	out_parags = []
	for i, (iTag, iTxt) in enumerate(myBodyDat):
		if clean_title:
			if ('UnitTitle' in iTag) or ('Title' in iTag):
				continue
		
		Util.check_unescaped_text(iTxt)
		assert iTxt.find('&') < 0
		myTxt = Util.xml_escape(iTxt)
		Util.check_escaped_text(myTxt)
		if myTxt != iTxt:
			lprint('{}\n\t{}\n\t{}\n'.format(myFid, iTxt, myTxt))
		
		out_sents = []
		# sentence segmentation
		sents = string_split(iTxt)
		for sid, sTxt in enumerate(sents):
			if sid == len(sents) - 1:  # last sentencein paragraph
				s_end = s_start + len(sTxt)
				out_sents.append({'sid': sid, 'text': sTxt, 'start': s_start, 'end': s_end})
				myLessonTxt += sTxt + sep_bar2
				s_start = s_end + len(sep_bar2)
			else:
				s_end = s_start + len(sTxt)
				out_sents.append({'sid': sid, 'text': sTxt, 'start': s_start, 'end': s_end})
				myLessonTxt += sTxt + sep_bar1
				s_start = s_end + len(sep_bar1)
		out_parags.append(out_sents)
	
	# read the questions
	assert p[1].tag == 'QAset'
	q_num = int(p[1].attrib['Num_Ques'])
	
	assert q_num == len(p[1]), 'question num incorrect'
	# lprint(myFid)
	q_dict = _qst2dat(p[1])
	
	myLessonTxt = myLessonTxt[:-3]  # clean the last "|||"
	return myFid, out_parags, myLessonTxt, q_dict


def str_lesson2parags(lesson_str):
	parags = lesson_str.split(sep_bar2)
	parags = [p.replace(sep_bar1, "") for p in parags]
	return parags


if __name__ == '__main__':
	from .. import config
	
	test_fp = config.DS_SSQA / "Develop" / "PubB-G6a-0302.xml"
	myFid, out_parags, myLessonTxt, q_dict = xml2st(test_fp)
	clean_parags = str_lesson2parags(myLessonTxt)
	
	print(clean_parags)
