import requests as req
from pprint import pprint
from lxml import html
from pymongo import MongoClient
import re
from time import gmtime, strftime

class ResponseData():

    @staticmethod
    def get_response_dom(link):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'}

        response = req.get(link, headers = headers)
        return html.fromstring(response.text)


class DbInitializer():
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client['news']

    def get_collection(self, name):
        return self.db[name]


class MailNewsParse():
    link_mail = 'https://news.mail.ru'

    def __init__(self):
        db_news = DbInitializer()
        self.news = db_news.get_collection('mail_news')

    def get_mail_news(self):
        dom = ResponseData.get_response_dom(self.link_mail)
        main_news_links = dom.xpath("//td[@class='daynews__main' or @class='daynews__items']"
                                    "//a[@class='photo photo_full photo_scale js-topnews__item' "
                                    "or @class='photo photo_small photo_scale photo_full js-topnews__item']/@href")

        for link in main_news_links:
            link = self.link_mail + link
            news_dom = ResponseData.get_response_dom(link)

            if not news_dom:
                return

            source = news_dom.xpath(".//div[@class='breadcrumbs breadcrumbs_article js-ago-wrapper']"
                                "//a[@class='link color_gray breadcrumbs__link']/span/text()")
            headers = news_dom.xpath(".//div[@class='hdr hdr_collapse hdr_bold_huge hdr_lowercase meta-speakable-title']"
                                "//h1/text()")
            date = news_dom.xpath(".//div[@class='breadcrumbs breadcrumbs_article js-ago-wrapper']"
                               "//span[@class='note__text breadcrumbs__text js-ago']/@datetime")
            dict = {}

            dict['link'] = link

            if len(source) > 0:
                dict['source'] = source
            if len(headers) > 0:
                dict['headers'] = headers
            if len(date) > 0:
                dict['date'] = date

            self.news.update_one({'link': dict['link']}, {'$set': dict}, upsert=True)

    def show_data(self):
        for item in self.news.find({}):
            pprint(item)


class LentaNewsParse():

    link_lenta = 'https://lenta.ru/'

    def __init__(self):
        db_news = DbInitializer()
        self.news = db_news.get_collection('lenta_news')

    def get_lenta_news(self):
        dom = ResponseData.get_response_dom(self.link_lenta)
        main_news_links = dom.xpath("//body/div[@id='root']/section[2]/div/div/div[1]/section[1]/div[1]/div |"
                                    "//body/div[@id='root']/section[2]/div/div/div[1]/section[1]/div[2]/div")
        for block in main_news_links:
            link = None
            header = None
            datetime = None
            dict = {}
            h2 = block.xpath("./h2")

            if len(h2) > 0:
                link = h2[0].xpath("./a/@href")
                header = h2[0].xpath("./a/text()")
                datetime = h2[0].xpath("./a/@datetime")
            else:
                link = block.xpath("./a/@href")
                header = block.xpath("./a/text()")
                datetime = block.xpath("./a/@datetime")

            if len(link) > 0:
                dict['link'] = self.link_lenta + link[0]
            else:
                continue

            if len(header) > 0:
                dict['header'] = header[0]

            if len (datetime) > 0:
                dict['datetime'] = datetime[0]

            self.news.update_one({'link': dict['link']}, {'$set': dict}, upsert=True)

    def show_data(self):
        for item in self.news.find({}):
            pprint(item)


class YandexNewsParse():
    link_yandex = 'https://yandex.ru'

    def __init__(self):
        db_news = DbInitializer()
        self.news = db_news.get_collection('yandex_news')

    def split_story_info(self, story_info):
        try:
            time = re.findall("\d{2}\:\d{2}$", story_info[0])[0]
            date = strftime("%Y-%m-%d", gmtime())
            return f'{date} {time}', re.findall("([\w\s\d\.]*) \d{2}\:\d{2}$", story_info[0])[0]
        except Exception as ex:
            print('Exc in method split_story_info. Class YandexNewsParse', ex)

    def get_yandex_news(self):

        dom = ResponseData.get_response_dom(self.link_yandex + "/news")
        main_news_dom = dom.xpath("//table[@class='stories-set__items']//td[@class='stories-set__item'] |"
                                  "//div[@class='stories-set__main-item']//div[@class='story__content']")

        for news in main_news_dom:
            dict = {}

            link = news.xpath(".//div[@class='story__topic']//h2[@class='story__title']//a/@href")
            if len(link) > 0:
                dict['link'] = self.link_yandex + link[0]
            else:
                continue

            headers = news.xpath(".//div[@class='story__topic']//h2[@class='story__title']//a/text()")
            if len(headers):
                dict['headers'] = headers[0]

            story_info = news.xpath('.//div[@class="story__info"]/div/text()')

            if len(story_info) > 0:
                dict['datetime'], dict['source'] = self.split_story_info(story_info)

            self.news.update_one({'link': dict['link']},
                                 {'$set': dict}, upsert=True)

    def show_data(self):
        for item in self.news.find({}):
            pprint(item)


if __name__ == '__main__':

    main_news = MailNewsParse()
    main_news.get_mail_news()
    main_news.show_data()

    yandex_news = YandexNewsParse()
    yandex_news.get_yandex_news()
    yandex_news.show_data()

    lenta_news = LentaNewsParse()
    lenta_news.get_lenta_news()
    lenta_news.show_data()
