from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from pymongo import MongoClient
import json
import hashlib


class mVideoParseSelenium:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        db = client.electronic_product
        self.collection = db['mVideo']
        chrome_options = Options()  # Выставляем опции драйвера и запускаем
        chrome_options.add_argument('start-maximized')
        self.driver = webdriver.Chrome(options=chrome_options)

    def load_dynamic_data(self):
        while True:
            try:
                button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((
                    By.XPATH, '//div[@class="gallery-layout"][2]//div[@class="accessories-carousel-wrapper"]'
                              '//a[@class = "next-btn sel-hits-button-next"]'
                )))
                if not button:
                    break
                button.click()
            except:
                break

    def init(self):
        self.driver.get('https://www.mvideo.ru')
        self.load_dynamic_data()
        elements = self.driver.find_elements_by_xpath('//div[@class="gallery-layout"][2]'
                                                  '//div[@class="accessories-carousel-wrapper"]//ul/li'
                                                  '//div[contains(@class, "product-tile-picture__holder")]/a')
        for elem in elements:
            text_attr = elem.get_attribute('data-product-info')
            link = elem.get_attribute('href')

            if not text_attr or not link:
                continue

            item = json.loads(text_attr)
            item['link'] = link

            hash_object = hashlib.md5(link.encode('utf-8'))
            id = hash_object.hexdigest()
            self.collection.update_one({'_id': id}, {'$set': item}, upsert=True)

        self.driver.quit()


if __name__ == "__main__":
    mvideo_parser = mVideoParseSelenium()
    mvideo_parser.init()
