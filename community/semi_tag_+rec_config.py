# -*- coding: utf-8 -*-
import os
import time

thisFilePath = os.path.split(os.path.realpath(__file__))[0]
# we have to modify the tail if we change the path of this python file
tail = 29
rootPath = thisFilePath[0:-tail]
if rootPath[-1] != "/" and rootPath[-1] != "\\":
    message = "Error root path [%s]\n\tPlease check whether you changed the path of current file" % rootPath
    raise Exception(message)
# print rootPath

data_root_path = rootPath

ALL_DOCKER_NAMES = None