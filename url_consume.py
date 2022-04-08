# -*- coding: utf-8 -*-#

# Author:ZephyrChole
# @software: PyCharm
# @file: url_consume.py
# @time: 2021/3/26 15:00
import idm.download
from threading import Thread


class URLConsumer(Thread):
    def __init__(self, repo, queue, id_, logger, downloader: idm.download.Downloader):
        super().__init__()
        self.repo = repo
        self.queue = queue
        self.id_ = id_
        self.logger = logger
        self.downloader = downloader

    def start(self) -> None:
        while True:
            v = self.queue.get()
            if v is False:
                self.queue.put(v)
                break
            else:
                download_url, name = v
                self.logger.info(f'url consumer{self.id_} <-- {name}')
                self.downloader.download_wait4file(download_url, name, self.repo, 60 * 10)

#
# def run(url_manager, log_setting, raw_urlQ, converted_urlQ, downloadQ, finishedQ, download_repo, additional_repos):
#     pool = Pool()
#     logger = get_logger('DownloadManager', log_setting)
#     FINISHED = True
#     while True:
#         if canContinue(converted_urlQ, downloadQ):
#             value = converted_urlQ.get()
#             if value == FINISHED:
#                 break
#             else:
#                 pool.apply_async(func=download,
#                                  args=(url_manager, log_setting, raw_urlQ, downloadQ, finishedQ, download_repo, value,
#                                        additional_repos))
#                 url_manager.notify(logger)
#         else:
#             time.sleep(randint(1, 10))
#     logger.info('download exit')
#
#
# def canContinue(download_url_queue, download_queue):
#     return not download_url_queue.empty() or not download_queue.empty()
#
#
# def download(url_manager, log_setting, raw_urlQ, downloadQ, finishedQ, download_repo, info: DownloadInfo,
#              additional_repos):
#     download_url, name, origin_url, size = info.download_url, info.name, info.origin_url, info.size
#
#     full_path = os.path.join(download_repo, name)
#     short_name = name[:6] if len(name) > 6 else name
#     logger = get_logger(short_name, log_setting)
#
#     logger.info(f'new download info: {name}')
#     if check_exists(logger, name, short_name, size, additional_repos + [download_repo], download_repo):
#         url_manager.remove_text_url(origin_url)
#     else:
#         downloadQ.put(origin_url)
#         logger.info(f'start download: {name}')
#         logger.debug(f'\nurl: {download_url}\norigin_url: {origin_url}')
#         url_manager.notify(logger)
#         parameters = ('wget', '--user-agent="Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0"',
#                       '--no-check-certificate', '-c', '-q', '-O', f'"{full_path}"', f'"{download_url}"')
#         try:
#             exitcode = Popen(' '.join(parameters), shell=True).wait(60 * 60)
#             logger.debug(f'exitcode: {exitcode} <-- {short_name}')
#
#             if exitcode == 0:
#                 url_manager.remove_text_url(origin_url)
#                 logger.info(f'download succeed: {short_name}')
#             else:
#                 raw_urlQ.put(origin_url)
#                 logger.info(f'download fail: {short_name}')
#         except Exception as e:
#             raw_urlQ.put(origin_url)
#             logger.warning(str(e))
#             logger.info(f'download fail: {short_name}')
#         downloadQ.get()
#         url_manager.notify(logger)
#     finishedQ.put(origin_url)
#
#
# def check_exists(logger, name, short_name, size, repos, download_repo):
#     isDownloaded = False
#     for repo in repos:
#         full_path = os.path.join(repo, name)
#         logger.info(f'check exist: {short_name} --> {repo}')
#         if os.path.exists(full_path):
#             if isDownloaded:
#                 os.remove(full_path)
#             elif full_download(full_path, size):
#                 logger.info(f'finished download: {short_name} --> {repo}')
#                 isDownloaded = True
#             elif repo == download_repo:
#                 logger.info(f'unfinished download: {short_name} --> {download_repo}')
#             else:
#                 os.remove(full_path)
#     return isDownloaded
#
#
# def full_download(path, size):
#     return os.path.getsize(path) / 1024 / 1024 > size
