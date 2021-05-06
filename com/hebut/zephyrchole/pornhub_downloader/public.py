# -*- coding: utf-8 -*-#

import logging
# Author:Jiawei Feng
# @software: PyCharm
# @file: public.py
# @time: 2021/5/6 17:48
import time


def get_logger(level, name):
    formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    fh = logging.FileHandler(f'./log/{time.strftime("%Y-%m-%d", time.localtime())}.log', encoding='utf-8')
    fh.setLevel(level)
    fh.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(fh)
    return logger
