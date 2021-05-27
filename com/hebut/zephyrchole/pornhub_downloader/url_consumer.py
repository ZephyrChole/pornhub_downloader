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


def run(download_url_queue: Queue, url_manager: UrlManager, download_repo, level, additional_repos):
    pool = Pool()
    logger = get_logger(level, 'DownloadManager')
    loop(download_url_queue, url_manager, download_repo, additional_repos, logger, pool, True)


def loop(download_url_queue, url_manager, download_repo, additional_repos, logger, pool, FINISHED):
    if canContinue(download_url_queue, url_manager.download_queue):
        value = download_url_queue.get()
        if value == FINISHED:
            logger.debug('下载线程收到结束信号,已退出')
            return True
        else:
            url, name, origin_url, size = value
            pool.apply_async(func=download,
                             args=(url_manager, download_repo, name, url, origin_url, size, additional_repos))
            url_manager.notify()
    else:
        time.sleep(randint(1, 10))
    return loop(download_url_queue, url_manager, download_repo, additional_repos, logger, pool, FINISHED)


def canContinue(download_url_queue, download_queue):
    return not download_url_queue.empty() or not download_queue.empty()


def download(url_manager, download_repo, name, url, text_url, size, additional_repos):
    url_manager.logger.debug(f'{name} 新下载进程')

    full_path = os.path.join(download_repo, name)
    if check_exists(url_manager.logger, name, size, iter(additional_repos + [download_repo]), download_repo):
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


def check_exists(logger, name, size, repos, download_repo, isDownloaded=False):
    try:
        repo = next(repos)
        full_path = os.path.join(repo, name)
        logger.debug(f'检查 {name} 是否在 {repo} 中')
        if os.path.exists(full_path):
            if isDownloaded:
                os.remove(full_path)
            elif full_download(full_path, size):
                logger.debug(f'{name} 在 {repo} 已完成')
                isDownloaded = True
            elif repo == download_repo:
                logger.info(f'{name} 在 {download_repo} 未完成,继续...')
            else:
                os.remove(full_path)
        return check_exists(logger, name, size, repos, download_repo, isDownloaded)
    except StopIteration:
        return isDownloaded


def full_download(path, size):
    return os.path.getsize(path) / 1024 / 1024 + 1 > size
