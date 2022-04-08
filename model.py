from public import get_browser
from selenium.common.exceptions import NoSuchElementException


class Model:
    def __init__(self, url_name):
        self.url_name = url_name
        self.urls = []

    def get_urls(self):
        if len(self.urls) == 0:
            browser = get_browser()
            browser.minimize_window()
            browser.get(f'https://cn.pornhub.com/model/{self.url_name}/videos')
            a = 0
            while True:
                a += 1
                try:
                    tar = browser.find_element_by_css_selector(
                        f'li.pcVideoListItem.js-pop.videoblock.videoBox:nth-child({a}) div div a')
                    self.urls.append(tar.get_attribute('href'))
                except NoSuchElementException:
                    break
            browser.close()
            print(f'model:{self.url_name} got {len(self.urls)} from Internet')
        return self.urls
