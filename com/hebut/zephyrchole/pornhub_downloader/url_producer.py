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

from com.hebut.zephyrchole.pornhub_downloader.url_manager import UrlManager, get_logger


def get_browser():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    return webdriver.Chrome(chrome_options=chrome_options)


def run(download_url_queue: Queue, url_manager: UrlManager, download_repo, level):
    def text_urls_not_empty():
        return len(url_manager.text_urls) > 0

    def download_pool_not_empty():
        return not url_manager.download_queue.empty()

    def produce_url_queue_not_empty():
        return not url_manager.produce_url_queue.empty()

    def download_queue_not_full():
        return url_manager.download_queue.qsize() + download_url_queue.qsize() < url_manager.pool_capacity

    browser = get_browser()
    logger = get_logger(level, 'UrlConverter')
    while text_urls_not_empty() or download_pool_not_empty():
        while produce_url_queue_not_empty() and download_queue_not_full():
            convert(logger, browser, download_repo, url_manager, download_url_queue)
        time.sleep(randint(1, 10))
    browser.quit()
    download_url_queue.put(True)


def convert(logger, browser, download_repo, url_manager, download_url_queue):
    url = url_manager.produce_url_queue.get()
    attempt = 0
    while attempt <= 3:
        try:
            download_url_queue.put(get_video_url_and_name(browser, logger, download_repo, url))
            break
        except Exception as e:
            attempt += 1
            logger.warning(str(e))
            logger.warning(f'重试{attempt}次')
            browser.quit()
            browser = get_browser()
    if attempt > 3:
        logger.info('重试3次,已跳过')
    url_manager.notify()


def enter_convert_page(browser, logger):
    browser.get('https://www.tubeoffline.com/download-PornHub-videos.php')
    logger.debug('enter convert_page')


def fill_in_url_and_click(browser, logger, url):
    WebDriverWait(browser, 30, 0.2).until(
        lambda x: x.find_element_by_css_selector('input.videoLink') and x.find_element_by_css_selector(
            'input.getVideo'))
    browser.find_element_by_css_selector('input.videoLink').send_keys(url)
    browser.find_element_by_css_selector('input.getVideo').click()
    logger.debug('fill in and click')


def get_url_and_name(browser, logger, repo, origin_url):
    def get_noname(repo):
        counter = 0
        while os.path.exists(os.path.join(repo, f'NoName{counter}')):
            counter += 1
        return f'NoName{counter}'

    def reformat_name(n):
        banned_symbols = ['?', '/', r'\\', ':', '*', '"', '<', '>', '|']
        return re.sub('|'.join(list(map(lambda x: f'[{x}]', banned_symbols))), '', n)

    WebDriverWait(browser, 30, 0.2).until(lambda x: x.find_element_by_css_selector(
        'div#videoDownload table tbody tr:last-child td:last-child a') and x.find_element_by_css_selector(
        'div#videoContainer'))
    download_url = browser.find_element_by_css_selector(
        'div#videoDownload table tbody tr:last-child td:last-child a').get_attribute('href')
    result = re.search('Title: (.+)', browser.find_element_by_css_selector('div#videoContainer').text)
    if result:
        name = result.group(1)
    else:
        name = get_noname(repo)
    name = reformat_name(f'{name}.mp4')
    browser.find_element_by_css_selector('tr:last-child td a.getSize1').click()
    while True:
        result = re.search('(\d+) MB', WebDriverWait(browser, 30, 0.2).until(
            lambda x: x.find_element_by_css_selector('tr:last-child td span')).text)
        if result:
            size = int(result.group(1))
            break
    logger.debug(f'converted info got.name:{name} url:{download_url} size:{size}')
    return download_url, name, origin_url, size


def get_video_url_and_name(browser, logger, download_repo, url):
    enter_convert_page(browser, logger)
    fill_in_url_and_click(browser, logger, url)
    return get_url_and_name(browser, logger, download_repo, url)
