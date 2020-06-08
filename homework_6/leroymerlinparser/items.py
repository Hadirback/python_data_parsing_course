# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import TakeFirst, MapCompose
import re


def convert_to_int(value):
    if value:
        return int(value)


def convert_to_float(value):
    if value:
        value = value.replace(" ", "")
        return float(value)


def cleaner_photo(value):
    if value[:2] == '//':
        return f'http:{value}'
    return value


def split_characteristics(value):
    characteristic = {}
    try:
        characteristic['name'] = value.xpath('./dt[@class="def-list__term"]/text()').extract_first()
        characteristic['value'] = formatting_string(value.xpath('./dd[@class="def-list__definition"]/text()').extract_first())
    except Exception as ex:
        print(f'split_characteristics - {ex}')
    return characteristic


def formatting_string(value):
    if value:
        value = re.sub("^\s+|\n|\r|\s+$", '', value)
        return value


class LeroymerlinparserItem(scrapy.Item):
    _id = scrapy.Field(input_processor=MapCompose(convert_to_int), output_processor=TakeFirst())
    name = scrapy.Field(output_processor=TakeFirst())
    photo = scrapy.Field(input_processor=MapCompose(cleaner_photo))
    price = scrapy.Field(input_processor=MapCompose(convert_to_float), output_processor=TakeFirst())
    currency = scrapy.Field(output_processor=TakeFirst())
    link = scrapy.Field(output_processor=TakeFirst())
    unit = scrapy.Field(output_processor=TakeFirst())
    characteristics = scrapy.Field(input_processor=MapCompose(split_characteristics))


