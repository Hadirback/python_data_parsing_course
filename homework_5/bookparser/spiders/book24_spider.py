# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from bookparser.items import BookparserItem

class Book24Spider(scrapy.Spider):
    name = 'book24'
    allowed_domains = ['book24.ru']

    def __init__(self, book):
        self.start_urls = [f'book24.ru/search/?q={book}']


    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//div[@class='catalog-pagination__list']/a[@class='catalog-pagination__item _text js-pagination-catalog-item']/@href").extract_first()
        book_links = response.xpath("//div[@class='catalog-products__item js-catalog-products-item']/a[@class='book__image-link js-item-element ddl_product_link']/@href").extract()

        for link in book_links:
            yield response.follow(link, callback=self.book_parse)

        yield response.follow(next_page, callback=self.parse)

    def book_parse(self, response: HtmlResponse):
        name = response.xpath("//div[@class='item-detail__informations-box']/h1[@class='item-detail__title']/text()").extract_first()
        authors = response.xpath("//div[@class='item-tab']//a[contains(@href,'author')]/text()").extract()
        publisher = response.xpath(
            "//div[@class='item-tab']//a[contains(@href,'brand')]/text()").extract_first()
        price = response.xpath(
            "//div[@class='item-actions__buttons-box']/div[@class='item-actions__price']/b/text()").extract_first()
        currency = response.xpath(
            "//div[@class='item-actions__buttons-box']/div[@class='item-actions__price']/text()").extract_first()
        rate = response.xpath("//div[@class='item-detail__information-item']//span[@class='rating__rate-value']/text()").extract_first()
        product_id = self.get_product_id(
            response.xpath("//div[@class='item-detail__wrapper js-product-card']/@data-product-id").extract_first())

        yield BookparserItem(name=name, authors=authors, publisher=publisher, price=price, currency=currency, rate=rate,
                             product_id=product_id)
