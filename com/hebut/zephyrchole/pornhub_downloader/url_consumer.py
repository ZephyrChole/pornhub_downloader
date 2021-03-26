# -*- coding: utf-8 -*-#

# Author:Jiawei Feng
# @software: PyCharm
# @file: url_consumer.py
# @time: 2021/3/26 15:00 


import logging
import os
from multiprocessing import Pool
from queue import Queue
from random import randint
from subprocess import Popen
from threading import Thread
from time import sleep

from url_manager import UrlManager


class DownloadManager(Thread):
    FINISHED = True

    def __init__(self, download_url_queue: Queue, url_manager: UrlManager, download_repo, level):
        Thread.__init__(self)
        self.download_url_queue = download_url_queue
        self.download_repo = download_repo
        self.url_manager = url_manager
        self.pool = Pool(self.url_manager.download_queue_max_length)
        self.init_logger(level)

    def init_logger(self, level):
        # init logger
        formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(formatter)
        self.logger = logging.getLogger('DownloadManager')
        self.logger.setLevel(level)
        self.logger.addHandler(ch)

    @staticmethod
    def download(url_manager, download_repo, name, url, text_url):
        url_manager.logger.debug('新下载进程')

        def check_for_exists(name, logger, full_path):
            def remove_old_files(full_path):
                os.remove(full_path)
                os.remove('{}.st'.format(full_path))

            logger.debug('检查 {} 是否在 {} 中'.format(name, download_repo))
            if os.path.exists(full_path):
                if os.path.exists('{}.st'.format(full_path)):
                    logger.info('发现未完成下载: {},已删除'.format(name))
                    remove_old_files(full_path)
                    return False
                else:
                    return True
            else:
                return False

        full_path = os.path.join(download_repo, name)
        if check_for_exists(name, url_manager.logger, full_path):
            url_manager.logger.info('发现已完成下载: {} ,已跳过'.format(name))
            url_manager.remove_text_url(text_url)
        else:
            url_manager.download_queue.put(text_url)
            url_manager.logger.info('开始新下载: {}'.format(name))
            url_manager.logger.debug('url:{} \norigin_url:{}'.format(url, text_url))
            url_manager.notify()
            a = Popen('axel -n 8 -q -o "{}" "{}"'.format(full_path, url), shell=True).wait()
            url_manager.logger.debug('下载完成，返回码: {}'.format(a))
            if a == False or a == 1:
                url_manager.produce_url_queue.put(text_url)
            else:
                url_manager.remove_text_url(text_url)
            url_manager.download_queue.get()
            url_manager.notify()

    def run(self):
        def download_url_queue_not_empty():
            return not self.download_url_queue.empty()

        def pool_length_not_zero():
            return self.url_manager.download_queue.qsize() > 0

        done = False
        while not done:
            while download_url_queue_not_empty() or pool_length_not_zero():
                value = self.download_url_queue.get()
                if value == self.FINISHED:
                    done = True
                    self.logger.debug('下载线程收到结束信号,已退出')
                    break
                url, name, origin_url = value
                self.pool.apply_async(func=self.download,
                                      args=(self.url_manager, self.download_repo, name, url, origin_url))
                self.url_manager.notify()
            sleep(randint(1, 10))
