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

from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from util import get_browser, has_keyword_file, get_logger


class URLProducer(Thread):
    def __init__(self, download_dir, download_queue, get_videos, id_, level, has_console, has_file,
                 refresh_url_file=None):
        super().__init__()
        self.download_dir = download_dir
        self.browser = get_browser()
        # self.browser.minimize_window()
        self.downloadQ = download_queue
        self.videos = get_videos()
        self.id_ = id_
        self.logger = get_logger(f'producer{self.id_}', level, has_console, has_file)
        self.whole_num = len(self.videos)
        self.refresh_url_file = refresh_url_file
        self.logger.debug(f'init')

    def run(self):
        def is_exist(dir_, n):
            return n is not None and has_keyword_file(dir_, n)

        self.logger.debug(f'start')
        while len(self.videos):
            if self.refresh_url_file is not None:
                self.refresh_url_file()

            v = self.videos.pop(random.randint(0, len(self.videos) - 1))
            self.logger.debug(f'got {v.url} {v.name}')
            url, name = v.url, v.name

            if is_exist(self.download_dir, name):
                self.logger.info(f'{self.whole_num - len(self.videos)}/{self.whole_num} >> {name}')
                continue
            try:
                self.enter_fill_click(self.browser, self.logger, url)
                download_url, name, origin_url = self.get_url_and_name(self.browser, self.logger, self.download_dir,
                                                                       url)
                self.downloadQ.put((download_url, name, origin_url))
                self.logger.info(
                    f'{self.whole_num - len(self.videos)}/{self.whole_num} --> {name}')
                time.sleep(1)
            except TimeoutException as e:
                self.logger.warning('TimeoutException' + str(e))
                self.videos.insert(0, v)
            except WebDriverException as e:
                self.logger.warning('WebDriverException' + str(e))
                self.browser = get_browser()
                self.videos.insert(0, v)
        # self.downloadQ.put(False)
        self.browser.close()
        self.logger.debug(f'exit')

    @staticmethod
    def enter_fill_click(browser, logger, url):
        # enter convert page
        browser.get('https://www.tubeoffline.com/download-PornHub-videos.php')
        logger.debug('enter convert_page')

        # fill in url and click
        WebDriverWait(browser, 30, 0.2).until(
            lambda x: x.find_element_by_css_selector('input.videoLink') and x.find_element_by_css_selector(
                'input.getVideo'))
        browser.find_element_by_css_selector('input.videoLink').send_keys(url)
        for i in range(1, 11):
            try:
                browser.find_element_by_css_selector('input#submitbutton').click()
                time.sleep(3)
            except NoSuchElementException:
                break
            logger.debug(f'click input {i} times')
        logger.debug('fill in and click')

    def get_url_and_name(self, browser, logger, repo, origin_url):
        WebDriverWait(browser, 30, 0.2).until(lambda x: x.find_element_by_css_selector(
            'div#videoDownload table tbody tr:last-child td:last-child a') and x.find_element_by_css_selector(
            'div#videoContainer'))
        download_url = browser.find_element_by_css_selector(
            'div#videoDownload table tbody tr:last-child td:last-child a').get_attribute('href')

        result = re.search('Title: (.+)', browser.find_element_by_css_selector('div#videoContainer').text)
        raw_name = result.group(1) if result else self.get_noname(repo)
        # reformat name
        banned_symbols = ['?', '/', r'\\', ':', '*', '"', '<', '>', '|']
        name = re.sub('|'.join(list(map(lambda x: f'[{x}]', banned_symbols))), repl='', string=f'{raw_name}.mp4')
        logger.debug(f'converted info got.name: {name} url: {download_url}')
        return download_url, name, origin_url

    @staticmethod
    def get_noname(repo):
        count = 0
        while True:
            if os.path.exists(os.path.join(repo, f'NoName{count}')):
                count += 1
            else:
                return f'NoName{count}'
