# -*- coding: utf-8 -*-#

# Author:Jiawei Feng
# @software: PyCharm
# @file: url_manager.py
# @time: 2021/3/26 15:00
import logging
import time


class UrlManager:

    def __init__(self, url_file_path, pool_capacity, level, download_url_queue, produce_url_queue, download_queue,
                 text_urls):
        self.url_file_path = url_file_path
        self.pool_capacity = pool_capacity
        self.download_queue = download_queue
        self.text_urls = text_urls
        self.produce_url_queue = produce_url_queue
        self.init_logger(level)
        self.read_in_urls(url_file_path)
        self.download_url_queue = download_url_queue

    def init_logger(self, level):
        # init logger
        formatter = logging.Formatter("%(asctime)s - %(message)s")
        fh = logging.FileHandler('./log/{}.log'.format(time.strftime("%Y-%m-%d", time.localtime())))
        fh.setLevel(level)
        fh.setFormatter(formatter)
        self.logger = logging.getLogger('UrlManager')
        self.logger.setLevel(level)
        self.logger.addHandler(fh)

    def read_in_urls(self, url_file_path):
        with open(url_file_path) as file:
            content = file.readlines()
            for url in content:
                url = url.strip()
                if len(url) > 0:
                    self.text_urls.append(url)
                    self.produce_url_queue.put(url)
        self.logger.info('从本地文件: {} 中读取了 {} 个链接'.format(self.url_file_path, len(self.text_urls)))

    def remove_text_url(self, url):
        self.text_urls.remove(url)
        with open(self.url_file_path, 'w') as file:
            for url in self.text_urls:
                file.write(url)
                file.write('\n')

    def notify(self):
        self.logger.info(
            '本地链接:{} 内存原链接:{} 下载队列:{} 下载链接缓存区:{}'.format(len(self.text_urls), self.produce_url_queue.qsize(),
                                                         self.download_queue.qsize(), self.download_url_queue.qsize()))
