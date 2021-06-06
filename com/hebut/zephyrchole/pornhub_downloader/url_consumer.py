# -*- coding: utf-8 -*-#

# Author:Jiawei Feng
# @software: PyCharm
# @file: url_consumer.py
# @time: 2021/3/26 15:00
import os
import time
from multiprocessing import Pool
from queue import Queue
from random import randint
from subprocess import Popen

from com.hebut.zephyrchole.pornhub_downloader.public import get_logger
from com.hebut.zephyrchole.pornhub_downloader.url_manager import UrlManager


def run(download_url_queue: Queue, url_manager: UrlManager, download_repo, level, additional_repos, hasConsole,
        hasFile):
    pool = Pool()
    logger = get_logger(level, 'DownloadManager', hasConsole, hasFile)
    logger.info('download manager start')
    FINISHED = True
    while True:
        if canContinue(download_url_queue, url_manager.download_queue):
            value = download_url_queue.get()
            if value == FINISHED:
                break
            else:
                url, name, origin_url, size = value
                pool.apply_async(func=download,
                                 args=(url_manager, download_repo, name, url, origin_url, size, additional_repos))
                url_manager.notify()
        else:
            time.sleep(randint(1, 10))
    logger.info('下载线程收到结束信号,已退出')


def canContinue(download_url_queue, download_queue):
    return not download_url_queue.empty() or not download_queue.empty()


def download(url_manager, download_repo, name, url, text_url, size, additional_repos):
    logger = url_manager.logger
    logger.info(f'新下载信息: {name}')

    full_path = os.path.join(download_repo, name)
    short_name = name[:6] if len(name) > 6 else name
    if check_exists(logger, name, short_name, size, additional_repos + [download_repo], download_repo):
        url_manager.remove_text_url(text_url)
    else:
        url_manager.download_queue.put(text_url)
        logger.info(f'开始新下载: {name}')
        logger.debug(f'\nurl: {url}\norigin_url: {text_url}')
        url_manager.notify()
        parameters = ('wget', '--user-agent="Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0"',
                      '--no-check-certificate', '-c', '-q', '-0', f'"{full_path}"', f'"{url}')
        try:
            exitcode = Popen(parameters, shell=True).wait(60 * 60)
            logger.debug(f'返回码: {exitcode} <-- {short_name}')

            if exitcode == 0:
                url_manager.remove_text_url(text_url)
                logger.info(f'下载成功: {short_name}')
                return True
            else:
                logger.info(f'下载失败: {short_name}')
            url_manager.download_queue.get()
        except Exception as e:
            logger.warning(str(e))
        url_manager.produce_url_queue.put(text_url)
        url_manager.notify()
        return False


def check_exists(logger, name, short_name, size, repos, download_repo):
    isDownloaded = False
    for repo in repos:
        full_path = os.path.join(repo, name)
        logger.info(f'检查库存: {short_name} --> {repo}')
        if os.path.exists(full_path):
            if isDownloaded:
                os.remove(full_path)
            elif full_download(full_path, size):
                logger.info(f'已完成下载: {short_name} --> {repo}')
                isDownloaded = True
            elif repo == download_repo:
                logger.info(f'未完成下载: {short_name} --> {download_repo}')
            else:
                os.remove(full_path)
    return isDownloaded


def full_download(path, size):
    return os.path.getsize(path) / 1024 / 1024 + 1 > size
