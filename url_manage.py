# -*- coding: utf-8 -*-#

# Author:ZephyrChole
# @software: PyCharm
# @file: url_manage.py
# @time: 2021/3/26 15:00
import os
import re
from util import Video


class URLManager:
    def __init__(self, url_file, logger):
        self.url_file = url_file
        self.back_up_path = f'{url_file}.bak'
        self.logger = logger
        self.videos = []
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
        self.logger.info(f'read in {len(self.videos)} url(s) <-- {self.url_file}')

    def read_in(self, url_file):
        urls = []
        with open(url_file) as file:
            content = file.readlines()
            for url in content:
                url = url.strip()
                if len(url) > 0 and re.match(r'https?://(cn|www)\.pornhub.com/view_video\.php\?viewkey=[a-zA-Z0-9]+',
                                             url):
                    urls.append(url)
        for url in set(urls):
            self.videos.append(Video(url))

    def get_videos(self):
        return self.videos

    def refresh_url_file(self):
        with open(self.url_file, 'w') as file:
            for v in self.videos:
                file.write(v.url + '\n')
