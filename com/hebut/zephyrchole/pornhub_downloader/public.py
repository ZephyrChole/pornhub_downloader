# -*- coding: utf-8 -*-#
# Author:Jiawei Feng
# @software: PyCharm
# @file: public.py
# @time: 2021/5/6 17:48
import logging
import time
from multiprocessing import Manager, Process
from os import mkdir
from os.path import exists

from com.hebut.zephyrchole.pornhub_downloader import url_consumer
from com.hebut.zephyrchole.pornhub_downloader import url_producer
from com.hebut.zephyrchole.pornhub_downloader.url_manager import UrlManager


def get_logger(level, name):
    formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    fh = logging.FileHandler(f'./log/{time.strftime("%Y-%m-%d", time.localtime())}.log', encoding='utf-8')
    fh.setLevel(level)
    fh.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(fh)
    return logger


def main(download_repo, url_file, level, pool_capacity=5, additional_repos=()):
    for repo in additional_repos:
        if not exists(repo):
            mkdir(repo)
    if not exists(download_repo):
        mkdir(download_repo)

    # global variables
    manager = Manager()
    download_url_queue = manager.Queue()
    download_queue = manager.Queue()
    text_urls = manager.list()
    produce_url_queue = manager.Queue()

    url_manager = UrlManager(url_file, pool_capacity, level, download_url_queue, produce_url_queue, download_queue,
                             text_urls)

    url_converter = Process(target=url_producer.run, args=(download_url_queue, url_manager, download_repo, level))
    downloader = Process(target=url_consumer.run,
                         args=(download_url_queue, url_manager, download_repo, level, additional_repos))
    url_converter.start()
    downloader.start()
    url_converter.join()
    downloader.join()
    print("已完成")
