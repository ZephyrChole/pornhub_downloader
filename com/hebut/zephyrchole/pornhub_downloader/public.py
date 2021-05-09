# -*- coding: utf-8 -*-#

# Author:Jiawei Feng
# @software: PyCharm
# @file: 1.py
# @time: 2021/5/9 19:22
import time
import logging


def get_logger(level, name):
    formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    fh = logging.FileHandler(f'./log/{time.strftime("%Y-%m-%d", time.localtime())}.log', encoding='utf-8')
    fh.setLevel(level)
    fh.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(fh)
    return logger
