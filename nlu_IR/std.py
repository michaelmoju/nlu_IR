import os, sys
import shutil
import logging


# Bunch pattern (see page 32 in "Python Algorithms: Mastering Basic Algorithms in the Python Language (2e) [Magnus Lie Hetland] (2014)")
class Bunch(dict):
	def __init__(self, *args, **kwds):
		super().__init__(*args, **kwds)
		self.__dict__ = self
        
        
def lprint(*args, **kwargs):
	import inspect
	callerFrame = inspect.stack()[1]  # 0 represents this line
	myInfo = inspect.getframeinfo(callerFrame[0])
	myFilename = os.path.basename(myInfo.filename)
	print('{}({}):'.format(myFilename, myInfo.lineno), *args, flush=True, file=sys.stderr, **kwargs)

    
def prompt(*args, **kwargs):
	print(*args, flush=True, **kwargs)


def new_dir(dir_path, clear=True):
	if os.path.exists(dir_path) and clear:
		prompt('Remove ' + dir_path)
		shutil.rmtree(dir_path)
	if not os.path.exists(dir_path):
		prompt('Create ' + dir_path)
		os.makedirs(dir_path)
        

def insist(expr, mesg=''):
	if not expr:
		if mesg: print(mesg)
		assert False
        
def log_w(filename, force=True):
	if not force:
		insist(not os.path.exists(filename), '{} exists!'.format(filename))
	myDir = os.path.dirname(filename)
	if myDir and not os.path.exists(myDir):
		os.makedirs(myDir)
	return logging.FileHandler(filename, 'w', 'utf-8')
        
        
def str2llv(s):
	# Level		Numeric value
	# CRITICAL  50
	# ERROR		40
	# WARNING   30
	# INFO		20
	# DEBUG		10
	# NOTSET	 0
    if isinstance(s, str):
        s = s.upper()
    if s == 'FATAL': return logging.FATAL
    if s == 'ERROR': return logging.ERROR
    if s == 'WARN': return logging.WARN
    if s == 'INFO': return logging.INFO
    if s == 'DEBUG': return logging.DEBUG
    if s == 'NOTSET': return logging.NOTSET
    try:
        return int(s)
    except ValueError:
        insist(False, 'Not able to convert "{}" to an integer!'.format(s))
