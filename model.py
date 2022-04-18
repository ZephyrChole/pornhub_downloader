from util import get_browser, Video
from selenium.common.exceptions import NoSuchElementException


class Model:
    def __init__(self, url_name, logger):
        self.url_name = url_name
        self.logger = logger
        self.videos = []

    def get_videos(self):
        if len(self.videos) == 0:
            browser = get_browser()
            browser.minimize_window()
            page_index = 1
            while True:
                if page_index == 1:
                    browser.get(f'https://cn.pornhub.com/model/{self.url_name}/videos')
                else:
                    browser.get(f'https://cn.pornhub.com/model/{self.url_name}/videos?page={page_index}')
                browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                browser.implicitly_wait(15)
                if page_index != 1 and '错误' in browser.find_element_by_css_selector('h1 span').text:
                    break
                video_index = 0
                while True:
                    video_index += 1
                    try:
                        tar = browser.find_element_by_css_selector(
                            f'li.pcVideoListItem.js-pop.videoblock.videoBox:nth-child({video_index}) div div a')
                        url, name = tar.get_attribute('href'), tar.get_attribute('data-title')
                        self.videos.append(Video(url, name))
                    except NoSuchElementException:
                        break
                page_index += 1
            browser.close()
            self.logger.info(f'model:{self.url_name} got {len(self.videos)} from Internet')
        return self.videos
