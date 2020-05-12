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

    myLogFormat = '%(asctime)s ***%(levelname)s*** [%(name)s:%(lineno)s] - %(message)s'
    logging.basicConfig(format=myLogFormat, datefmt='%Y/%m/%d %H:%M:%S', level=str2llv(args.llv))
    if args.log:
        logger.addHandler(log_w(args.log))
        logger.log(100, ' '.join(sys.argv))
    else:
        logger.log(100, ' '.join(sys.argv))
        

if __name__ == '__main__':
    main()