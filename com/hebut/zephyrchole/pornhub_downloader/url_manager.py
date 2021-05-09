# -*- coding: utf-8 -*-#

# Author:Jiawei Feng
# @software: PyCharm
# @file: url_manager.py
# @time: 2021/3/26 15:00
import os
from com.hebut.zephyrchole.pornhub_downloader.public import get_logger


class UrlManager:
    def __init__(self, url_file_path, pool_capacity, level, download_url_queue, produce_url_queue, download_queue,
                 text_urls):
        self.url_file_path = url_file_path
        self.back_up_path = f'{url_file_path}.bak'
        self.pool_capacity = pool_capacity
        self.download_queue = download_queue
        self.text_urls = text_urls
        self.produce_url_queue = produce_url_queue
        self.logger = get_logger(level, 'UrlManager')
        self.read_in_urls(url_file_path)
        self.download_url_queue = download_url_queue

    def read_in_urls(self, url_file_path):
        if os.path.exists(self.back_up_path):
            self.read_in(self.back_up_path)
            if os.path.exists(url_file_path):
                os.remove(url_file_path)
            os.rename(self.back_up_path, url_file_path)
        else:
            self.read_in(url_file_path)
            if os.path.exists(self.back_up_path):
                os.remove(self.back_up_path)
        self.logger.info(f'从本地文件: {self.url_file_path} 中读取了 {len(self.text_urls)} 个链接')

    def read_in(self, url_file_path):
        with open(url_file_path) as file:
            content = file.readlines()
            for url in content:
                url = url.strip()
                if len(url) > 0:
                    self.text_urls.append(url)
                    self.produce_url_queue.put(url)

    def remove_text_url(self, url):
        self.text_urls.remove(url)
        self.copy_file(self.url_file_path, self.back_up_path)
        with open(self.url_file_path, 'w') as file:
            for url in self.text_urls:
                file.write(url)
                file.write('\n')
        os.remove(self.back_up_path)

    def copy_file(self, src, dst):
        os.system(f'cp {src} {dst}')

    def notify(self):
        self.logger.info(
            f'本地链接:{len(self.text_urls)} 内存原链接:{self.produce_url_queue.qsize()} 下载队列:{self.download_queue.qsize()} 下载链接缓存区:{self.download_url_queue.qsize()}')
