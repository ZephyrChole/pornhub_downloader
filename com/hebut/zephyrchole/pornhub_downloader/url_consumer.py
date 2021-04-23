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

from com.hebut.zephyrchole.pornhub_downloader.url_manager import UrlManager, get_logger


def full_download(path, size):
    return os.path.getsize(path) / 1024 / 1024 + 1 > size


def check_exists(logger, download_repo, name, size, additional_repos):
    full_downloaded = False
    for repo in additional_repos + [download_repo]:
        full_path = os.path.join(repo, name)
        logger.debug(f'检查 {name} 是否在 {repo} 中')
        if os.path.exists(full_path):
            if full_downloaded:
                os.remove(full_path)
            elif full_download(full_path, size):
                logger.debug(f'{name} 在 {repo} 已完成')
                full_downloaded = True
            elif repo == download_repo:
                logger.info(f'{name} 在 {download_repo} 未完成,继续...')
            else:
                os.remove(full_path)
    return full_downloaded


def download(url_manager, download_repo, name, url, text_url, size, additional_repos):
    url_manager.logger.debug(f'{name} 新下载进程')

    full_path = os.path.join(download_repo, name)
    if check_exists(url_manager.logger, download_repo, name, size, additional_repos):
        url_manager.remove_text_url(text_url)
    else:
        url_manager.download_queue.put(text_url)
        url_manager.logger.info(f'开始新下载: {name}')
        url_manager.logger.debug(f'{name} url:{url} \norigin_url:{text_url}')
        url_manager.notify()
        exitcode = Popen(
            f'wget --user-agent="Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0" --no-check-certificate -c -q -O "{full_path}" "{url}"',
            shell=True).wait()
        url_manager.logger.debug(f'返回码: {name} {exitcode}')

        if exitcode == 0:
            url_manager.remove_text_url(text_url)
            url_manager.logger.info(f'下载成功 {name}')
        else:
            url_manager.produce_url_queue.put(text_url)
            url_manager.logger.info(f'下载失败 {name}')
        url_manager.download_queue.get()
        url_manager.notify()


def run(download_url_queue: Queue, url_manager: UrlManager, download_repo, level, additional_repos):
    pool = Pool(url_manager.pool_capacity)
    logger = get_logger(level, 'DownloadManager')
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
                             args=(url_manager, download_repo, name, url, origin_url, size, additional_repos))
            url_manager.notify()
            time.sleep(randint(1, 10))
        time.sleep(randint(1, 10))
