#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
import re
import xml.sax.saxutils
from collections import Counter

from ..std import *

from . import Const

_log = logging.getLogger(__name__)

# Due to backward compatibility, '//' is used to separate Word-POS pair.
# Since a word may consists of '//' (such as http://www.cwb.gov.tw), the following regular expression is used to split a Word-POS pair.
_rgx = re.compile(r'^(.*)//([^/]*)$')

# SSQA text should not consist of the following ASCII chars
_rgx_chk_unescaped = re.compile(r'([\t\r\n#$&\'*<?@^_`{|}])')
_rgx_chk_escaped = re.compile(r'([\t\r\n#$\'*<>?@^_`{|}])')
# SSQA text should not consist of the following strings
_rgx_chk_str = re.compile(r'(\|\||&&)')
_rgx_ckip_rel_headline = re.compile(r'(.*)\[(\d+)\]\s+(.*)#')


# I will use the following strings as separators for SSQA system
#	'{', '}', '|', '||', '|||', ...
# Although the texts of SSQA corpus do not consist of SPACE character (i.e., ' '),
# I will not use ' ' as a separator because ordinary English texts consist of a lot of SPACE characters.


def check_unescaped_text(txt):
	m = _rgx_chk_unescaped.search(txt)
	if m:
		eprint('\n"{}"\nconsists of [{}]'.format(txt, m.group(0)))
		raise ValueError
	m = _rgx_chk_str.search(txt)
	if m:
		eprint('\n"{}"\nconsists of [{}]'.format(txt, m.group(0)))
		raise ValueError


def check_escaped_text(txt):
	m = _rgx_chk_escaped.search(txt)
	if m:
		eprint('\n"{}"\nconsists of [{}]'.format(txt, m.group(0)))
		raise ValueError
	m = _rgx_chk_str.search(txt)
	if m:
		eprint('\n"{}"\nconsists of [{}]'.format(txt, m.group(0)))
		raise ValueError


def xml_escape(txt):
	# xml.sax.saxutils.escape(data, entities={})
	# Escape '&', '<', and '>' in a string of data.
	return xml.sax.saxutils.escape(txt)
