# -*- coding: utf-8 -*-#

# Author:ZephyrChole
# @software: PyCharm
# @file: main.py
# @time: 2021/3/26 15:50
import logging
from com.hebut.zephyrchole.pornhub_downloader.start import main

if __name__ == '__main__':
    main(download_repo='./unsorted', url_file='./input.txt', level=logging.INFO,
         pool_capacity=5, additional_repos=[], hasConsole=True, hasFile=False)
