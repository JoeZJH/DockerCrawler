# -*- coding: utf-8 -*-

import logging


log_format = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)-8s: %(message)s'

logging.basicConfig(level=logging.DEBUG,
                    format=log_format,
                    datefmt='%d %b %Y %H:%M:%S',
                    filename='myapp.log.txt',
                    filemode='a')

# output the log whose level is higher than INFO to Std output
console = logging.StreamHandler()
console.setLevel(logging.WARNING)
formatter = logging.Formatter(log_format)
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

logging.info('\n\n########################## NEW_LOG ########################\n')
