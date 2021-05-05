# -*- coding: utf-8 -*-#

# Author:Jiawei Feng
# @software: PyCharm
# @file: pornhub_downloader.py
# @time: 2021/3/26 15:50
import logging

import com.hebut.zephyrchole.pornhub_downloader.pornhub_downloader as pd


def main():
    pd.main('/media/pi/sda1/media/porn/unsorted', './input.txt', logging.DEBUG, ['/media/pi/sda1/media/porn/repo'])


if __name__ == '__main__':
    main()
