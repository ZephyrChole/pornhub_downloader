# -*- coding: utf-8 -*-#
# Author:Jiawei Feng
# @software: PyCharm
# @file: public.py
# @time: 2021/5/6 17:48
from multiprocessing import Manager, Process
from os import mkdir
from os.path import exists

from com.hebut.zephyrchole.pornhub_downloader import url_consumer
from com.hebut.zephyrchole.pornhub_downloader import url_producer
from com.hebut.zephyrchole.pornhub_downloader.url_manager import UrlManager


def main(download_repo, url_file, level, pool_capacity=5, additional_repos=(), hasConsole=True, hasFile=False):
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
                             text_urls, hasConsole, hasFile)

    url_converter = Process(target=url_producer.run,
                            args=(download_url_queue, url_manager, download_repo, level, hasConsole, hasFile))
    downloader = Process(target=url_consumer.run,
                         args=(download_url_queue, url_manager, download_repo, level, additional_repos, hasConsole,
                               hasFile))
    url_converter.start()
    downloader.start()
    url_converter.join()
    downloader.join()
