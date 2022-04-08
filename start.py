# -*- coding: utf-8 -*-#
# Author:ZephyrChole
# @software: PyCharm
# @file: public.py
# @time: 2021/5/6 17:48
import logging
from idm.download import Downloader
from url_consume import URLConsumer
from url_produce import URLProducer
from url_manage import URLManager
from queue import Queue
from public import get_logger


def main(download_dir, url_file, idm_path, level=logging.INFO, has_console=True, has_file=False):
    downloader = Downloader(idm_path)
    downloadQ = Queue()
    logger = get_logger('pornhub download', level, has_console, has_file)
    manager = URLManager(url_file, logger)
    producer = URLProducer(download_dir, downloadQ, manager.get_urls, manager.refresh_url_file, logger)
    consumers = [URLConsumer(download_dir, downloadQ, i, logger, downloader) for i in range(5)]
    producer.start()
    for c in consumers:
        c.start()
    producer.join()
    for c in consumers:
        c.join()
