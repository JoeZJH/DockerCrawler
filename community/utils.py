#-*- coding: utf-8 -*-
#encoding=utf-8
import time
import logging

def get_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


logformat = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)-8s: %(message)s'

logging.basicConfig(level=logging.DEBUG,
                    format=logformat,
                    datefmt='%d %b %Y %H:%M:%S',
                    filename='myapp.log.txt',
                    filemode='a')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter(logformat)
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

logging.info('ZHOUJIAHONG##########################NEW_LOG########################')