# -*- coding: utf-8 -*-#
# Author:ZephyrChole
# @software: PyCharm
# @file: util.py
# @time: 2021/5/6 17:48
import os
import random
import logging
from idm.download import Downloader
from url_consume import URLConsumer
from url_produce import URLProducer
from url_manage import URLManager
from queue import Queue
from util import get_logger, check_path, get_browser
from model import Model
from info_cacher.main import InfoCacher


class URLManagerNoFile:
    def __init__(self, videos):
        self.videos = videos

    def get_videos(self):
        return self.videos


def get_model_names(file):
    with open(file) as file:
        content = file.readlines()
    model_names = list(map(lambda x: x.strip(), content))
    model_names = list(filter(lambda x: x, model_names))
    model_names = list(set(model_names))
    return model_names


class MultiModel:
    def __init__(self, model_file, download_dir, idm, level=logging.INFO, has_console=True, has_file=False):
        self.model_names = get_model_names(model_file)
        self.download_dir = download_dir
        self.downloader = idm
        self.logger = get_logger('pornhub download', level, has_console, has_file)
        self.has_console = has_console
        self.has_file = has_file

    def load_cache(self):
        cacher = InfoCacher('./', 'pornhub')
        if cacher.has_valid_cache:
            models = []
            old = cacher.loads()
            old_name_to_self = {m.url_name: m for m in old}
            for name in self.model_names:
                model = old_name_to_self.get(name)
                if model is None:
                    models.append(Model(name, self.logger))
                else:
                    model.logger = self.logger
                    models.append(model)
        else:
            models = list(map(lambda name: Model(name, self.logger), self.model_names))

        input('now turn on the proxy')
        browser = get_browser()
        # browser.minimize_window()
        for m in models:
            m.get_videos(browser)
        browser.close()
        cacher.dumps(models)
        input('now turn off the proxy')
        return models

    def main(self, produce_pool=1, consume_pool=5):
        models = self.load_cache()
        random.shuffle(models)
        check_path(self.download_dir)
        for m in models:
            downloadQ = Queue()
            manager = URLManagerNoFile(m.get_videos())
            model_dir = os.path.join(self.download_dir, m.url_name)
            producers = [URLProducer(model_dir, downloadQ, manager.get_videos, i, self.has_console, self.has_file) for i
                         in range(produce_pool)]
            # download_dir, download_queue, get_videos, id_, has_console, has_file, refresh_url_file = None
            # repo, queue, downloader: idm.download.Downloader, id_, has_console, has_file
            consumers = [URLConsumer(model_dir, downloadQ, self.downloader, i, self.has_console, self.has_file) for i in
                         range(consume_pool)]
            for p in producers:
                p.start()
            for c in consumers:
                c.start()
            for p in producers:
                p.join()
            for c in consumers:
                c.join()


def main(download_dir, url_file, idm_path, produce_pool, consume_pool, level=logging.INFO, has_console=True,
         has_file=False):
    downloader = Downloader(idm_path)
    downloadQ = Queue()
    logger = get_logger('pornhub download', level, has_console, has_file)
    manager = URLManager(url_file, logger)
    producers = [URLProducer(download_dir, downloadQ, manager.get_videos, i, has_console, has_file) for i
                 in range(produce_pool)]
    # download_dir, download_queue, get_videos, id_, has_console, has_file, refresh_url_file = None
    # repo, queue, downloader: idm.download.Downloader, id_, has_console, has_file
    consumers = [URLConsumer(download_dir, downloadQ, downloader, i, has_console, has_file) for i in
                 range(consume_pool)]
    for p in producers:
        p.start()
    for c in consumers:
        c.start()
    for p in producers:
        p.join()
    for c in consumers:
        c.join()
