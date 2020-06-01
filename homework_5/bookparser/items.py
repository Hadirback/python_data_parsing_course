# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BookparserItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    authors = scrapy.Field()
    publisher = scrapy.Field()
    price = scrapy.Field()
    currency = scrapy.Field()
    rate = scrapy.Field()
    product_id = scrapy.Field()

