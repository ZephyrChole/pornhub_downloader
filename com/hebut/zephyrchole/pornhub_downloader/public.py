# -*- coding: utf-8 -*-#

# Author:ZephyrChole
# @software: PyCharm
# @file: 1.py
# @time: 2021/5/9 19:22
import sys
import time
import logging


def get_logger(level, name, hasConsole, hasFile):
    formatter = logging.Formatter("%(asctime)s - %(filename)s - %(levelname)s: %(message)s")
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if hasConsole:
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(level)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    if hasFile:
        fh = logging.FileHandler(f'./log/{time.strftime("%Y-%m-%d", time.localtime())}.log', encoding='utf-8')
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    return logger
