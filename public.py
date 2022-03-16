# -*- coding: utf-8 -*-#

# Author:ZephyrChole
# @software: PyCharm
# @file: 1.py
# @time: 2021/5/9 19:22
import sys
import time
import logging


class LogSetting:
    def __init__(self, level: logging.INFO, hasConsole, hasFile):
        self.level = level
        self.hasConsole = hasConsole
        self.hasFile = hasFile


def get_logger(name, log_setting: LogSetting):
    level = log_setting.level
    hasConsole = log_setting.hasConsole
    hasFile = log_setting.hasFile

    formatter = logging.Formatter("%(asctime)s %(filename)s %(levelname)s: %(message)s")
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
