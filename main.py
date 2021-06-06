# -*- coding: utf-8 -*-#

# Author:Jiawei Feng
# @software: PyCharm
# @file: main.py
# @time: 2021/3/26 15:50
import logging
from com.hebut.zephyrchole.pornhub_downloader.start import main

if __name__ == '__main__':
    main(download_repo='/media/pi/sda1/media/porn/unsorted', url_file='./input.txt', level=logging.DEBUG,
         pool_capacity=5, additional_repos=['/media/pi/sda1/media/porn/repo'], hasConsole=True, hasFile=False)
