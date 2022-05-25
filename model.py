import time

from util import get_browser, Video
from selenium.common.exceptions import NoSuchElementException, MoveTargetOutOfBoundsException
from selenium.webdriver.common.action_chains import ActionChains


class Model:
    def __init__(self, url_name, logger):
        self.url_name = url_name
        self.logger = logger
        self.videos = []

    @property
    def need_get_videos(self):
        return len(self.videos) == 0

    def get_videos(self, br=None):
        if len(self.videos) == 0:
            if br is None:
                browser = get_browser()
                # browser.minimize_window()
            else:
                browser = br
            page_index = 1
            while True:
                if page_index == 1:
                    browser.get(f'https://cn.pornhub.com/model/{self.url_name}/videos')
                else:
                    browser.get(f'https://cn.pornhub.com/model/{self.url_name}/videos?page={page_index}')
                browser.implicitly_wait(15)
                try:
                    if page_index != 1 and '错误' in browser.find_element_by_css_selector('h1 span').text:
                        break
                except NoSuchElementException:
                    pass
                for i in range(1, 4):
                    try:
                        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        break
                    except:
                        self.logger.warning(f'scroll fail{i}')
                video_index = 0
                while True:
                    video_index += 1
                    try:
                        tar = browser.find_element_by_css_selector(
                            f'ul#mostRecentVideosSection li.pcVideoListItem.js-pop.videoblock.videoBox:nth-child({video_index}) div div a')
                        for i in range(1, 11):
                            try:
                                ActionChains(browser).move_to_element(tar).perform()
                            except MoveTargetOutOfBoundsException:
                                self.logger.debug(f'video {video_index} wait hover {i} times')
                                time.sleep(3)
                        time.sleep(1)
                        url, name = tar.get_attribute('href'), tar.get_attribute('data-title')
                        self.logger.debug(f'{url}, {name}')
                        self.videos.append(Video(url, name))
                    except NoSuchElementException as e:
                        print(e)
                        break
                page_index += 1
            if br is None:
                browser.close()
            has_name_num = 0
            for v in self.videos:
                if v.name != '' and v.name != None:
                    has_name_num += 1
            self.logger.info(f'model:{self.url_name} {has_name_num}/{len(self.videos)} has_name/whole from Internet')
        return self.videos
