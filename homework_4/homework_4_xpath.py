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

            source = news_dom.xpath("//div[@class='breadcrumbs breadcrumbs_article js-ago-wrapper']"
                                "//a[@class='link color_gray breadcrumbs__link']/span/text()")
            headers = news_dom.xpath("//div[@class='hdr hdr_collapse hdr_bold_huge hdr_lowercase meta-speakable-title']"
                                "//h1/text()")
            date = news_dom.xpath("//div[@class='breadcrumbs breadcrumbs_article js-ago-wrapper']"
                               "//span[@class='note__text breadcrumbs__text js-ago']/@datetime")
            dict = {}

            dict['link'] = link

            if len(source) > 0:
                dict['source'] = source
            if len(headers) > 0:
                dict['headers'] = headers
            if len(date) > 0:
                dict['date'] = date

            self.news.update_one({'link': dict['link']},
                                        {'$set': dict}, upsert=True)



class LentaNewsParse():

    link_lenta = 'https://lenta.ru/'

class YandexNewsParse():

    link_yandex = 'https://yandex.ru'

    def __init__(self):
        db_news = DbInitializer()
        self.news = db_news.get_collection('yandex_news')

    def get_yandex_news(self):

        dom = ResponseData.get_response_dom(self.link_yandex + "/news")
        main_news_dom = dom.xpath("//div[@class='stories-set__main-item']//div[@class='story__topic'] | "
                                  "//table[@class='stories-set__items']//div[@class='story__topic']")

        length = len(main_news_dom)

        for i in range(0, length - 1):
            story_info = main_news_dom[i].xpath("//div[@class='story__info']/div/text()")[0]

            if not story_info:
                continue

            dict = {}

            link = main_news_dom[i].xpath("//div[@class='story__topic']//h2[@class='story__title']//a/@href")[0]
            dict['link'] = self.link_yandex + link
            dict['headers'] = main_news_dom[i].xpath("//div[@class='story__topic']//h2[@class='story__title']//a/text()")[0]

            time = re.findall("\d{2}\:\d{2}$", story_info)[0]

            date = strftime("%Y-%m-%d", gmtime())
            dict['datetime'] = f'{date} {time}'
            dict['source'] = re.findall("([\w\s\d\.]*) \d{2}\:\d{2}$", story_info)[0]

            self.news.update_one({'link': dict['link']},
                                 {'$set': dict}, upsert=True)


if __name__ == '__main__':
    #main_news = MailNewsParse()
    #main_news.get_mail_news()

    yandex_news = YandexNewsParse()
    yandex_news.get_yandex_news()


    db_news = DbInitializer()
    #mail_news = db_news.get_collection('mail_news')



    #for item in mail_news.find({}):
    #    pprint(item)


    yandex_news = db_news.get_collection('yandex_news')
    for item in yandex_news.find({}):
        pprint(item)