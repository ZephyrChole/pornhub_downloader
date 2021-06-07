# -*- coding: utf-8 -*-#
# Author:ZephyrChole
# @software: PyCharm
# @file: public.py
# @time: 2021/5/6 17:48
import os
from multiprocessing import Manager, Process

from com.hebut.zephyrchole.pornhub_downloader import url_consumer
from com.hebut.zephyrchole.pornhub_downloader import url_producer
from com.hebut.zephyrchole.pornhub_downloader.url_manager import UrlManager
from com.hebut.zephyrchole.pornhub_downloader.public import LogSetting


def check_path(dir_path):
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        return True
    else:
        path = os.path.split(dir_path)[0]
        if check_path(path):
            try:
                os.mkdir(dir_path)
                return True
            except:
                return False
        else:
            return False


def main(download_repo, url_file, level, pool_capacity=5, additional_repos=(), hasConsole=True, hasFile=False):
    for repo in additional_repos:
        if not check_path(repo): return 1
    if not check_path(download_repo): return 1

    # global variables
    manager = Manager()
    text_urlL = manager.list()
    raw_urlQ = manager.Queue()
    converting_urlQ = manager.Queue()
    converted_urlQ = manager.Queue()
    downloadQ = manager.Queue()
    log_setting = LogSetting(level, hasConsole, hasFile)

    url_manager = UrlManager(url_file, log_setting, pool_capacity, text_urlL, raw_urlQ, converting_urlQ, converted_urlQ,
                             downloadQ)

    url_converter = Process(target=url_producer.run,
                            args=(url_manager, log_setting, pool_capacity, text_urlL, raw_urlQ, converting_urlQ,
                                  converted_urlQ, downloadQ, download_repo))
    downloader = Process(target=url_consumer.run,
                         args=(url_manager, log_setting, raw_urlQ, converted_urlQ, downloadQ, download_repo,
                               additional_repos))
    url_converter.start()
    downloader.start()
    url_converter.join()
    downloader.join()
