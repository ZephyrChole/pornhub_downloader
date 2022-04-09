from util import get_browser, Video
from selenium.common.exceptions import NoSuchElementException


class Model:
    def __init__(self, url_name):
        self.url_name = url_name
        self.videos = []

    def get_videos(self):
        if len(self.videos) == 0:
            browser = get_browser()
            browser.minimize_window()
            browser.get(f'https://cn.pornhub.com/model/{self.url_name}/videos')
            a = 0
            while True:
                a += 1
                try:
                    tar = browser.find_element_by_css_selector(
                        f'li.pcVideoListItem.js-pop.videoblock.videoBox:nth-child({a}) div div a')
                    url, name = tar.get_attribute('href'), tar.get_attribute('data-title')
                    self.videos.append(Video(url, name))
                except NoSuchElementException:
                    break
            browser.close()
            print(f'model:{self.url_name} got {len(self.videos)} from Internet')
        return self.videos
