import logging
from .std import *


logging.basicConfig(format = '%(asctime)s ***%(levelname)s*** [%(name)s:%(lineno)s] - %(message)s',
                    datefmt = '%Y/%m/%d %H:%M:%S',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-llv', 
                        default='INFO', 
                        help='Logging level')
    parser.add_argument('-log',
                        default=None,
                        help='Output log file')
    
    args = parser.parse_args()
    
    if myArg.log:
        myFormat = '%(asctime)s ***%(levelname)s*** [%(name)s:%(lineno)s] - %(message)s'
        logging.basicConfig(format=myFormat, datefmt = '%Y/%m/%d %H:%M:%S', handlers=[log_w(args.log)], level=str2llv(myArg.llv))
        _log.log(100, ' '.join(sys.argv))
    else:
        myFormat = '%(filename)s(%(lineno)d): %(message)s'
        logging.basicConfig(level=str2llv(myArg.llv), format=myFormat)
        _log.log(100, ' '.join(sys.argv))

if __name__ == '__main__':
    main()