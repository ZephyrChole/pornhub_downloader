# -*- coding: utf-8 -*-#
# Author:ZephyrChole
# @software: PyCharm
# @file: util.py
# @time: 2021/5/6 17:48
import os
import logging
from idm.download import Downloader
from url_consume import URLConsumer
from url_produce import URLProducer
from url_manage import URLManager
from queue import Queue
from util import get_logger
from model import Model


class URLManagerNoFile:
    def __init__(self, videos):
        self.videos = videos

    def get_videos(self):
        return self.videos


def start_from_model_file(model_file, download_dir, idm_path, level=logging.INFO, has_console=True,
                          has_file=False):
    input('now turn on the proxy')
    logger = get_logger('pornhub download', level, has_console, has_file)
    with open(model_file) as file:
        content = file.readlines()
    model_names = list(map(lambda x: x.strip(), content))
    model_names = list(filter(lambda x: x, model_names))
    model_names = set(model_names)
    models = list(map(lambda name: Model(name, logger), model_names))
    for m in models:
        m.get_videos()
    input('now turn off the proxy')
    downloader = Downloader(idm_path)
    for m in models:
        downloadQ = Queue()
        manager = URLManagerNoFile(m.get_videos())
        model_dir = os.path.join(download_dir, m.url_name)
        producer = URLProducer(model_dir, downloadQ, manager.get_videos, logger)
        consumers = [URLConsumer(model_dir, downloadQ, i, logger, downloader) for i in range(5)]
        producer.start()
        for c in consumers:
            c.start()
        producer.join()
        for c in consumers:
            c.join()


def main(download_dir, url_file, idm_path, level=logging.INFO, has_console=True, has_file=False):
    downloader = Downloader(idm_path)
    downloadQ = Queue()
    logger = get_logger('pornhub download', level, has_console, has_file)
    manager = URLManager(url_file, logger)
    producer = URLProducer(download_dir, downloadQ, manager.get_videos, logger, manager.refresh_url_file)
    consumers = [URLConsumer(download_dir, downloadQ, i, logger, downloader) for i in range(5)]
    producer.start()
    for c in consumers:
        c.start()
    producer.join()
    for c in consumers:
        c.join()
