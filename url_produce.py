# -*- coding: utf-8 -*-#

# Author:ZephyrChole
# @software: PyCharm
# @file: url_produce.py
# @time: 2021/3/26 14:59
import os
import re
import time
import random
import logging
from threading import Thread

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait


class URLProducer(Thread):
    def __init__(self, download_dir, download_queue, get_urls, refresh_url_file, logger: logging):
        super().__init__()
        self.download_dir = download_dir
        self.logger = logger
        self.browser = get_browser()
        self.browser.minimize_window()
        self.downloadQ = download_queue
        self.raw_urls = get_urls()
        self.whole_num = len(self.raw_urls)
        self.refresh_url_file = refresh_url_file
        self.logger.debug(f'url producer init')

    def run(self):
        self.logger.debug(f'url producer start')
        while len(self.raw_urls):
            url = self.raw_urls.pop(random.randint(0, len(self.raw_urls) - 1))
            self.refresh_url_file()
            download_url, name = get_video_url_and_name(self.browser, self.logger, self.download_dir, url)
            self.downloadQ.put((download_url, name))
            self.logger.info(f'url producer --> {name} progress:{self.whole_num - len(self.raw_urls)}/{self.whole_num}')
            time.sleep(1)
        self.downloadQ.put(False)
        self.browser.close()
        self.logger.debug('url producer exit')


def get_browser(headless=False):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    return webdriver.Chrome(chrome_options=chrome_options)


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
    logger.debug(f'converted info got.name: {name} url: {download_url}')
    return download_url, name
    # browser.find_element_by_css_selector('tr:last-child td a.getSize1').click()
    # size = get_size(browser)
    # if not size:
    #     logger.warning(f'{origin_url} cannot get size')
    # logger.debug(f'converted info got.name: {name} url: {download_url} size: {size}M')


def get_noname(repo, count=0):
    if os.path.exists(os.path.join(repo, f'NoName{count}')):
        return get_noname(repo, count + 1)
    else:
        return f'NoName{count}'


#
# def get_size(browser, attempt=0):
#     result = re.search('(\d+) MB', WebDriverWait(browser, 30, 0.2).until(
#         lambda x: x.find_element_by_css_selector('tr:last-child td span')).text)
#     if result:
#         return int(result.group(1))
#     elif attempt <= 100:
#         return get_size(browser, attempt + 1)
#     else:
#         return 10 * 6
#
# def run(url_manager, log_setting, pool_capacity, text_urlL, raw_urlQ, converting_urlQ, converted_urlQ, downloadQ,
#         download_repo):
#     logger = get_logger('UrlConverter', log_setting)
#     browser = get_browser()
#     while not isDone(text_urlL, downloadQ):
#         if canContinue(raw_urlQ, downloadQ, converted_urlQ, pool_capacity):
#             attempt = 0
#             url = raw_urlQ.get()
#             converting_urlQ.put(url)
#             url_manager.notify(logger)
#
#             while attempt < 3:
#                 attempt += 1
#                 try:
#                     converted_urlQ.put(get_video_url_and_name(browser, logger, download_repo, url))
#                     break
#                 except Exception as e:
#                     logger.warning(str(e))
#                     logger.warning(f'retry {attempt}')
#                     browser.quit()
#
#             converting_urlQ.get()
#             if attempt == 3:
#                 logger.warning('retry 3 times,skip')
#                 raw_urlQ.put(url)
#             url_manager.notify(logger)
#         else:
#             time.sleep(randint(1, 10))
#     browser.quit()
#     converted_urlQ.put(True)
#
#
# def isDone(text_urls, download_queue):
#     return len(text_urls) == 0 and download_queue.empty()
#
#
# def canContinue(produce_url_queue, download_queue, download_url_queue, pool_capacity):
#     return not produce_url_queue.empty() and not isFullDownloadQueue(download_queue, download_url_queue, pool_capacity)


def isFullDownloadQueue(download_queue, download_url_queue, pool_capacity):
    return download_queue.qsize() + download_url_queue.qsize() == pool_capacity
