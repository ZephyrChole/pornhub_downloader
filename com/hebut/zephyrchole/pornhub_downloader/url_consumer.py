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

from com.hebut.zephyrchole.pornhub_downloader.url_manager import UrlManager


class DownloadManager(Thread):
    FINISHED = True

    def __init__(self, download_url_queue: Queue, url_manager: UrlManager, download_repo, level):
        Thread.__init__(self)
        self.download_url_queue = download_url_queue
        self.download_repo = download_repo
        self.url_manager = url_manager
        self.pool = Pool(self.url_manager.pool_capacity)
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
    def download(url_manager, download_repo, name, url, text_url, size):
        url_manager.logger.debug('{} 新下载进程'.format(name))

        def check_for_exists(name, logger, full_path):
            def full_downloaded(p, s):
                return os.path.getsize(p) / 1024 / 1024 + 1 < s

            logger.debug('检查 {} 是否在 {} 中'.format(name, download_repo))
            if os.path.exists(full_path):
                if full_downloaded(full_path, size):
                    logger.info('发现未完成下载: {},继续...'.format(name))
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
            url_manager.logger.debug('{} url:{} \norigin_url:{}'.format(name, url, text_url))
            url_manager.notify()
            exitcode = Popen(
                'wget --user-agent="Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0" --no-check-certificate -c -q -O "{}" "{}"'.format(
                    full_path, url), shell=True).wait()
            url_manager.logger.debug('{} 返回码: {}'.format(name, exitcode))

            if exitcode == True or exitcode == 0:
                url_manager.remove_text_url(text_url)
                url_manager.logger.info('{} 下载成功'.format(name))
            else:
                url_manager.produce_url_queue.put(text_url)
                url_manager.logger.info('{} 下载失败'.format(name))
            url_manager.download_queue.get()
            url_manager.notify()

    def run(self):
        def download_url_queue_not_empty():
            return not self.download_url_queue.empty()

        def pool_length_not_zero():
            return not self.url_manager.download_queue.empty()

        done = False
        while not done:
            while download_url_queue_not_empty() or pool_length_not_zero():
                value = self.download_url_queue.get()
                if value == self.FINISHED:
                    done = True
                    self.logger.debug('下载线程收到结束信号,已退出')
                    break
                url, name, origin_url, size = value
                self.pool.apply_async(func=self.download,
                                      args=(self.url_manager, self.download_repo, name, url, origin_url, size))
                self.url_manager.notify()
            sleep(randint(1, 10))


def get_logger(level):
    # init logger
    formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger = logging.getLogger('DownloadManager')
    logger.setLevel(level)
    logger.addHandler(ch)
    return logger


def download(url_manager, download_repo, name, url, text_url, size):
    url_manager.logger.debug('{} 新下载进程'.format(name))

    def check_for_exists(name, logger, full_path):
        def full_downloaded(p, s):
            return os.path.getsize(p) / 1024 / 1024 + 0.1 < s

        logger.debug('检查 {} 是否在 {} 中'.format(name, download_repo))
        if os.path.exists(full_path):
            if full_downloaded(full_path, size):
                logger.info('发现未完成下载: {},继续...'.format(name))
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
        url_manager.logger.debug('{} url:{} \norigin_url:{}'.format(name, url, text_url))
        url_manager.notify()
        exitcode = Popen(
            'wget --user-agent="Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0" --no-check-certificate -c -q -O "{}" "{}"'.format(
                full_path, url), shell=True).wait()
        url_manager.logger.debug('{} 返回码: {}'.format(name, exitcode))

        if exitcode == True or exitcode == 0:
            url_manager.remove_text_url(text_url)
            url_manager.logger.info('{} 下载成功'.format(name))
        else:
            url_manager.produce_url_queue.put(text_url)
            url_manager.logger.info('{} 下载失败'.format(name))
        url_manager.download_queue.get()
        url_manager.notify()


def run(download_url_queue: Queue, url_manager: UrlManager, download_repo, level):
    pool = Pool(url_manager.pool_capacity)
    logger = get_logger(level)
    FINISHED = True

    def download_url_queue_not_empty():
        return not download_url_queue.empty()

    def pool_length_not_zero():
        return not url_manager.download_queue.empty()

    done = False
    while not done:
        while download_url_queue_not_empty() or pool_length_not_zero():
            value = download_url_queue.get()
            if value == FINISHED:
                done = True
                logger.debug('下载线程收到结束信号,已退出')
                break
            url, name, origin_url, size = value
            pool.apply_async(func=download,
                             args=(url_manager, download_repo, name, url, origin_url, size))
            url_manager.notify()
        sleep(randint(1, 10))
