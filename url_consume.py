# -*- coding: utf-8 -*-#

# Author:ZephyrChole
# @software: PyCharm
# @file: url_consume.py
# @time: 2021/3/26 15:00
import os
from threading import Thread
import idm.download
from util import has_keyword_file, check_path


class URLConsumer(Thread):
    def __init__(self, repo, queue, id_, logger, downloader: idm.download.Downloader):
        super().__init__()
        self.repo = repo
        self.queue = queue
        self.id_ = id_
        self.logger = logger
        self.downloader = downloader
        self.logger.debug(f'consumer{self.id_} init')
        check_path(self.repo)

    def run(self) -> None:
        self.logger.debug(f'consumer{self.id_} start')
        while True:
            v = self.queue.get()
            if v is False:
                self.queue.put(v)
                self.logger.debug(f'consumer{self.id_} exit')
                break
            else:
                download_url, name, origin_url = v
                self.logger.info(f'consumer{self.id_} <-- {name}')
                if has_keyword_file(self.repo, name):
                    self.logger.info(f'consumer{self.id_}: {name} already exists,skipped')
                elif self.downloader.download_wait4file(download_url, name, self.repo, 60 * 10) is False:
                    with open(os.path.join(self.repo, 'fail_urls.txt'), 'a') as file:
                        file.write(origin_url + '\n')
