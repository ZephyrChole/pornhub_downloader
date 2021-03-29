# -*- coding: utf-8 -*-#

# Author:Jiawei Feng
# @software: PyCharm
# @file: pornhub_downloader.py
# @time: 2021/3/26 15:00

import logging
from os import mkdir
from os.path import exists
from multiprocessing import Manager,Process

from com.hebut.zephyrchole.pornhub_downloader import url_consumer
from com.hebut.zephyrchole.pornhub_downloader import url_producer
from com.hebut.zephyrchole.pornhub_downloader.url_manager import UrlManager


def main(download_repo, url_file, pool_capacity=5, level='INFO'):
    if not exists(download_repo):
        mkdir(download_repo)
    level_dic = {'INFO': logging.INFO, 'DEBUG': logging.DEBUG, 'WARNING': logging.WARNING, 'ERROR': logging.ERROR}
    level = level_dic.get(level, logging.INFO)

    # global variables
    manager = Manager()
    download_url_queue = manager.Queue()
    download_queue = manager.Queue()
    text_urls = manager.list()
    produce_url_queue = manager.Queue()

    url_manager = UrlManager(url_file, pool_capacity, level, download_url_queue, produce_url_queue, download_queue,
                             text_urls)

    url_converter = Process(target=url_producer.run, args=(download_url_queue, url_manager, download_repo, level))
    downloader = Process(target=url_consumer.run, args=(download_url_queue, url_manager, download_repo, level))
    url_converter.start()
    downloader.start()
    url_converter.join()
    downloader.join()
    print("已完成")


if __name__ == '__main__':
    main('../unsorted', './input.txt')
