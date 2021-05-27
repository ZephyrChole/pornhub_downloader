# -*- coding: utf-8 -*-#

# Author:Jiawei Feng
# @software: PyCharm
# @file: url_producer.py
# @time: 2021/3/26 14:59

import os
import re
import time
from queue import Queue
from random import randint

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait

from com.hebut.zephyrchole.pornhub_downloader.url_manager import UrlManager
from com.hebut.zephyrchole.pornhub_downloader.public import get_logger


def run(download_url_queue: Queue, url_manager: UrlManager, download_repo, level):
    browser = get_browser()
    logger = get_logger(level, 'UrlConverter')
    loop(download_url_queue, url_manager, download_repo, logger, browser)


def loop(download_url_queue: Queue, url_manager: UrlManager, download_repo, logger, browser):
    if not isDone(url_manager.text_urls, url_manager.download_queue):
        if canContinue(url_manager.produce_url_queue, url_manager.download_queue, download_url_queue,
                       url_manager.pool_capacity):
            convert(logger, browser, download_repo, url_manager, download_url_queue)
        else:
            time.sleep(randint(1, 10))
        return loop(download_url_queue, url_manager, download_repo, logger, browser)
    else:
        browser.quit()
        download_url_queue.put(True)
        return True


def isDone(text_urls, download_queue):
    return len(text_urls) == 0 and download_queue.empty()


def canContinue(produce_url_queue, download_queue, download_url_queue, pool_capacity):
    return not produce_url_queue.empty() and not isFullDownloadQueue(download_queue, download_url_queue, pool_capacity)


def isFullDownloadQueue(download_queue, download_url_queue, pool_capacity):
    return download_queue.qsize() + download_url_queue.qsize() == pool_capacity


def get_browser():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    return webdriver.Chrome(chrome_options=chrome_options)


def convert(logger, browser, download_repo, url_manager, download_url_queue, attempt=0):
    if attempt <= 3:
        url = url_manager.produce_url_queue.get()
        try:
            download_url_queue.put(get_video_url_and_name(browser, logger, download_repo, url))
        except Exception as e:
            logger.warning(str(e))
            logger.warning(f'重试{attempt}次')
            browser.quit()
            convert(logger, get_browser(), download_repo, url_manager, download_url_queue, attempt + 1)
    else:
        logger.info('重试3次,已跳过')
        url_manager.notify()


def get_video_url_and_name(browser, logger, download_repo, url):
    # enter convert page
    browser.get('https://www.tubeoffline.com/download-PornHub-videos.php')
    logger.debug('enter convert_page')

    # fill in url and click
    WebDriverWait(browser, 30, 0.2).until(
        lambda x: x.find_element_by_css_selector('input.videoLink') and x.find_element_by_css_selector(
            'input.getVideo'))
    browser.find_element_by_css_selector('input.videoLink').send_keys(url)
    browser.find_element_by_css_selector('input.getVideo').click()
    logger.debug('fill in and click')

    return get_url_and_name(browser, logger, download_repo, url)


def get_url_and_name(browser, logger, repo, origin_url):
    WebDriverWait(browser, 30, 0.2).until(lambda x: x.find_element_by_css_selector(
        'div#videoDownload table tbody tr:last-child td:last-child a') and x.find_element_by_css_selector(
        'div#videoContainer'))
    download_url = browser.find_element_by_css_selector(
        'div#videoDownload table tbody tr:last-child td:last-child a').get_attribute('href')

    result = re.search('Title: (.+)', browser.find_element_by_css_selector('div#videoContainer').text)
    raw_name = result.group(1) if result else get_noname(repo)
    # reformat name
    banned_symbols = ['?', '/', r'\\', ':', '*', '"', '<', '>', '|']
    name = re.sub('|'.join(list(map(lambda x: f'[{x}]', banned_symbols))), repl='', string=f'{raw_name}.mp4')

    browser.find_element_by_css_selector('tr:last-child td a.getSize1').click()
    size = get_size(browser)
    logger.debug(f'converted info got.name:{name} url:{download_url} size:{size}')
    return download_url, name, origin_url, size


def get_noname(repo, count=0):
    if os.path.exists(os.path.join(repo, f'NoName{count}')):
        return get_noname(repo, count + 1)
    else:
        return f'NoName{count}'


def get_size(browser):
    result = re.search('(\d+) MB', WebDriverWait(browser, 30, 0.2).until(
        lambda x: x.find_element_by_css_selector('tr:last-child td span')).text)
    if result:
        return int(result.group(1))
    else:
        return get_size(browser)
