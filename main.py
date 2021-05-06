# -*- coding: utf-8 -*-#

# Author:Jiawei Feng
# @software: PyCharm
# @file: main.py
# @time: 2021/3/26 15:50
import logging

from com.hebut.zephyrchole.pornhub_downloader.public import main

main('/media/pi/sda1/media/porn/unsorted', './input.txt', logging.DEBUG, 5, ['/media/pi/sda1/media/porn/repo'])
