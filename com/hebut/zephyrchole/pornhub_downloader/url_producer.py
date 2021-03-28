# -*- coding: utf-8 -*-#

# Author:Jiawei Feng
# @software: PyCharm
# @file: url_producer.py
# @time: 2021/3/26 14:59

import logging
import os
import re
import time
from queue import Queue
from random import randint
from threading import Thread

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait

from com.hebut.zephyrchole.pornhub_downloader.url_manager import UrlManager


class UrlConverter(Thread):
    def __init__(self, download_url_queue: Queue, url_manager: UrlManager, download_repo, level):
        Thread.__init__(self)
        self.download_url_queue = download_url_queue
        self.url_manager = url_manager
        self.download_repo = download_repo
        self.init_logger(level)
        self.init_browser()

    def init_browser(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        self.browser = webdriver.Chrome(chrome_options=chrome_options)

    def init_logger(self, level):
        formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(formatter)
        self.logger = logging.getLogger('UrlConverter')
        self.logger.setLevel(level)
        self.logger.addHandler(ch)

    def run(self):
        def text_urls_not_empty():
            return len(self.url_manager.text_urls) > 0

        def download_pool_not_empty():
            return not self.url_manager.download_queue.empty()

        def produce_url_queue_not_empty():
            return not self.url_manager.produce_url_queue.empty()

        def download_queue_not_full():
            return self.url_manager.download_queue.qsize() + self.download_url_queue.qsize() < self.url_manager.pool_capacity

        while text_urls_not_empty() or download_pool_not_empty():
            while produce_url_queue_not_empty() and download_queue_not_full():
                self.convert()
            time.sleep(randint(1, 10))
        self.close()

    def convert(self):
        url = self.url_manager.produce_url_queue.get()
        attempt = 0
        while attempt <= 3:
            try:
                self.download_url_queue.put(self.get_video_url_and_name(url))
                break
            except Exception as e:
                attempt += 1
                self.logger.warning(str(e))
                self.logger.warning('重试{}次'.format(attempt))
                self.init_browser()
        if attempt > 3:
            self.logger.info('重试3次,已跳过')
        self.url_manager.notify()
        time.sleep(randint(1, 10))

    def get_video_url_and_name(self, url):

        def enter_convert_page(br, log):
            br.get('https://www.tubeoffline.com/download-PornHub-videos.php')
            log.debug('entered convert_page')

        def fill_in_url_and_click(br, log, url):
            WebDriverWait(br, 30, 0.2).until(
                lambda x: x.find_element_by_css_selector('input.videoLink') and x.find_element_by_css_selector(
                    'input.getVideo'))
            br.find_element_by_css_selector('input.videoLink').send_keys(url)
            br.find_element_by_css_selector('input.getVideo').click()
            log.debug('fill in and click')

        def get_url_and_name(br, log, repo, origin_url):
            def get_noname(repo):
                counter = 0
                while os.path.exists(os.path.join(repo, 'NoName{}'.format(counter))):
                    counter += 1
                return 'NoName{}'.format(counter)

            def reformat_name(n):
                banned_symbols = ['?', '/', r'\\', ':', '*', '"', '<', '>', '|']
                return re.sub('|'.join(list(map(lambda x: '[{}]'.format(x), banned_symbols))), '', n)

            WebDriverWait(br, 30, 0.2).until(lambda x: x.find_element_by_css_selector(
                'div#videoDownload table tbody tr:last-child td:last-child a') and x.find_element_by_css_selector(
                'div#videoContainer'))
            download_url = br.find_element_by_css_selector(
                'div#videoDownload table tbody tr:last-child td:last-child a').get_attribute('href')
            result = re.search('Title: (.+)', br.find_element_by_css_selector('div#videoContainer').text)
            if result:
                name = result.group(1)
            else:
                name = get_noname(repo)
            name = reformat_name('{}.mp4'.format(name))
            br.find_element_by_css_selector('tr:last-child td a.getSize1').click()
            while True:
                result = re.search('(\d+) MB', WebDriverWait(br, 30, 0.2).until(
                    lambda x: x.find_element_by_css_selector('tr:last-child td span')).text)
                if result:
                    size = int(result.group(1))
                    break
            log.debug('converted info got.name:{} url:{}'.format(name, download_url))
            return download_url, name, origin_url, size

        enter_convert_page(self.browser, self.logger)
        fill_in_url_and_click(self.browser, self.logger, url)
        return get_url_and_name(self.browser, self.logger, self.download_repo, url)

    def close(self):
        self.browser.quit()
        self.download_url_queue.put(True)


def get_browser():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    return webdriver.Chrome(chrome_options=chrome_options)


def get_logger(level):
    formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger = logging.getLogger('UrlConverter')
    logger.setLevel(level)
    logger.addHandler(ch)
    return logger


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
    logger = get_logger(level)
    while text_urls_not_empty() or download_pool_not_empty():
        while produce_url_queue_not_empty() and download_queue_not_full():
            convert(logger, browser, download_repo, url_manager, download_url_queue)
        time.sleep(randint(1, 10))
    close(browser, download_url_queue)


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
            logger.warning('重试{}次'.format(attempt))
            browser = get_browser()
    if attempt > 3:
        logger.info('重试3次,已跳过')
    url_manager.notify()
    time.sleep(randint(1, 10))


def get_video_url_and_name(browser, logger, download_repo, url):
    def enter_convert_page(br, log):
        br.get('https://www.tubeoffline.com/download-PornHub-videos.php')
        log.debug('entered convert_page')

    def fill_in_url_and_click(br, log, url):
        WebDriverWait(br, 30, 0.2).until(
            lambda x: x.find_element_by_css_selector('input.videoLink') and x.find_element_by_css_selector(
                'input.getVideo'))
        br.find_element_by_css_selector('input.videoLink').send_keys(url)
        br.find_element_by_css_selector('input.getVideo').click()
        log.debug('fill in and click')

    def get_url_and_name(br, log, repo, origin_url):
        def get_noname(repo):
            counter = 0
            while os.path.exists(os.path.join(repo, 'NoName{}'.format(counter))):
                counter += 1
            return 'NoName{}'.format(counter)

        def reformat_name(n):
            banned_symbols = ['?', '/', r'\\', ':', '*', '"', '<', '>', '|']
            return re.sub('|'.join(list(map(lambda x: '[{}]'.format(x), banned_symbols))), '', n)

        WebDriverWait(br, 30, 0.2).until(lambda x: x.find_element_by_css_selector(
            'div#videoDownload table tbody tr:last-child td:last-child a') and x.find_element_by_css_selector(
            'div#videoContainer'))
        download_url = br.find_element_by_css_selector(
            'div#videoDownload table tbody tr:last-child td:last-child a').get_attribute('href')
        result = re.search('Title: (.+)', br.find_element_by_css_selector('div#videoContainer').text)
        if result:
            name = result.group(1)
        else:
            name = get_noname(repo)
        name = reformat_name('{}.mp4'.format(name))
        br.find_element_by_css_selector('tr:last-child td a.getSize1').click()
        while True:
            result = re.search('(\d+) MB', WebDriverWait(br, 30, 0.2).until(
                lambda x: x.find_element_by_css_selector('tr:last-child td span')).text)
            if result:
                size = int(result.group(1))
                break
        log.debug('converted info got.name:{} url:{}'.format(name, download_url))
        return download_url, name, origin_url, size

    enter_convert_page(browser, logger)
    fill_in_url_and_click(browser, logger, url)
    return get_url_and_name(browser, logger, download_repo, url)


def close(browser, download_url_queue):
    browser.quit()
    download_url_queue.put(True)
