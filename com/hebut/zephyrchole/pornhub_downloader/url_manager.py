# -*- coding: utf-8 -*-#

# Author:ZephyrChole
# @software: PyCharm
# @file: url_manager.py
# @time: 2021/3/26 15:00
import os
import re
from shutil import copyfile
from com.hebut.zephyrchole.pornhub_downloader.public import get_logger


class UrlManager:
    def __init__(self, url_file, log_setting, pool_capacity, text_urlL, raw_urlQ, converting_urlQ, converted_urlQ,
                 downloadQ, finishedQ):
        self.url_file = url_file
        self.back_up_path = f'{url_file}.bak'
        self.logger = get_logger('UrlManager', log_setting)
        self.pool_capacity = pool_capacity
        self.text_urlL = text_urlL
        self.raw_urlQ = raw_urlQ
        self.converting_urlQ = converting_urlQ
        self.converted_urlQ = converted_urlQ
        self.downloadQ = downloadQ
        self.finishedQ = finishedQ
        self.read_in_urls(url_file)

    def read_in_urls(self, url_file):
        if os.path.exists(self.back_up_path):
            self.read_in(self.back_up_path)
            if os.path.exists(url_file):
                os.remove(url_file)
            os.rename(self.back_up_path, url_file)
        else:
            self.read_in(url_file)
            if os.path.exists(self.back_up_path):
                os.remove(self.back_up_path)
        self.logger.info(f'read in {len(self.text_urlL)} url(s) <-- {self.url_file}')

    def read_in(self, url_file):
        with open(url_file) as file:
            content = file.readlines()
            for url in content:
                url = url.strip()
                if len(url) > 0 and re.match(r'https?://(cn|www)\.pornhub.com/view_video\.php\?viewkey=[a-zA-Z0-9]+',
                                             url):
                    self.text_urlL.append(url)
                    self.raw_urlQ.put(url)

    def remove_text_url(self, url):
        self.text_urlL.remove(url)
        copyfile(self.url_file, self.back_up_path)
        with open(self.url_file, 'w') as file:
            for url in self.text_urlL:
                file.write(url)
                file.write('\n')
        os.remove(self.back_up_path)

    def notify(self, logger):
        logger.info(
            f'text:{len(self.text_urlL)} raw:{self.raw_urlQ.qsize()} converting:{self.converting_urlQ.qsize()} converted:{self.converted_urlQ.qsize()} download:{self.downloadQ.qsize()} finished:{self.finishedQ.qsize()}')
