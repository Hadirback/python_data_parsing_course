# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from bookparser.items import BookparserItem
import re


class LabirintSpider(scrapy.Spider):
    name = 'labirint'
    allowed_domains = ['labirint.ru']

    def __init__(self, book):
        self.start_urls = [f'https://www.labirint.ru/search/{book}/?stype=0']

    def parse(self, response: HtmlResponse):
        next_page = response.css('a.pagination-next__text::attr(href)').extract_first()
        book_links = response.xpath("//div[@class='product-cover']/a[@class='product-title-link']/@href").extract()

        for link in book_links:
            yield response.follow(link, callback=self.book_parse)

        yield response.follow(next_page, callback=self.parse)

    def get_product_id(self, product_id_string):
        try:
            if product_id_string:
                return re.findall('[\d]+$',product_id_string)[0]
        except Exception as ex:
            print(ex)

    def book_parse(self, response: HtmlResponse):
        name = response.xpath("//div[@id='product-title']/h1/text()").extract_first()
        authors = response.xpath("//div[@class='product-description']/div[@class='authors']/text()").extract()
        publisher = response.xpath("//div[@class='product-description']/div[@class='publisher']/a/text()").extract_first()
        price = response.xpath("//div[@class='product-description']/div[@class='buying']//span[@class='buying-price-val-number']/text()").extract_first()
        currency = response.xpath("//div[@class='product-description']/div[@class='buying']//span[@class='buying-pricenew-val-currency']/text()").extract_first()
        rate = response.xpath("//div[@id='rate']/text()").extract_first()
        product_id = self.get_product_id(response.xpath("//div[@class='product-description']//div[@class='articul']/text()").extract_first())

        yield BookparserItem(name=name, authors=authors, publisher=publisher, price=price, currency=currency, rate=rate, product_id=product_id)