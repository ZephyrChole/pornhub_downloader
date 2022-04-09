# -*- coding: utf-8 -*-#

# Author:ZephyrChole
# @software: PyCharm
# @file: 1.py
# @time: 2021/5/9 19:22
import os
import sys
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class Video:
    def __init__(self, url, name=None):
        self.url = url
        self.name = name


def is_exist(dir_, name):
    for i in os.listdir(dir_):
        if name in i:
            return True
    return False


def get_browser(headless=False):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    return webdriver.Chrome(chrome_options=chrome_options)


def check_path(dir_path):
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        return True
    else:
        path = os.path.split(dir_path)[0]
        if check_path(path):
            try:
                os.mkdir(dir_path)
            except FileExistsError:
                return False
            except OSError:
                return False
        else:
            return False


def get_logger(name, level, has_console=False, has_file=False):
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if has_console:
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(level)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    if has_file:
        count = 0
        module_log_path = './log'
        check_path(module_log_path)
        while True:
            path = os.path.join(module_log_path, f'{time.strftime("%Y-%m-%d", time.localtime())}-{count}.log')
            if os.path.exists(path):
                count += 1
            else:
                break
        fh = logging.FileHandler(path, encoding='utf-8')
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    return logger
