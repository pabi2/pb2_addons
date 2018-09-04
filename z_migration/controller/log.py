# -*- coding: utf-8 -*-
"""
Create log files
# Reference source code
https://gist.githubusercontent.com/mcdeid/ccd7c00e9ae9a80e45297abb7b06ea1d/raw/8f8423e066228779b8129e8bca836dcde8bdcece/log.py
"""
import logging
import os
import time


def setup_custom_logger(filename):
    module_dir = \
        os.path.dirname(os.path.realpath(__file__)).split('/controller')[0]
    log_path = '%s/logs/%s_%s.log' \
        % (module_dir, filename, time.strftime('%Y_%m_%d_%H_%M_%S'))
    formatter = logging.Formatter(
        fmt='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    sthandler = logging.StreamHandler()
    sthandler.setFormatter(formatter)
    flhandler = logging.FileHandler(log_path)
    flhandler.setFormatter(formatter)
    logger = logging.getLogger('root')
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        logger.addHandler(sthandler)
        logger.addHandler(flhandler)
    else:
        logger.info('Handlers already added to logger.')
    logger.info('Log created at level: ' + str(logger.getEffectiveLevel()))
    return logger
