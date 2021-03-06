# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import scrapy
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline
import hashlib
import os

class LeroymerlinparserPipeline:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.leroymerlin

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        collection.update_one({'_id': item["_id"]}, {'$set': item}, upsert=True)
        return item


class LeroymerlinPhotoPipelines(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photo']:
            for img in item['photo']:
                try:
                    yield scrapy.Request(img, meta={'item': item})
                except Exception as ex:
                    print(ex)

    def item_completed(self, results, item, info):
        if results:
            item['photo'] = [itm[1] for itm in results if itm[0]]
        return item

    def file_path(self, request, response=None, info=None):
        item = request.meta['item']  # Используя meta, вытаскиваем данные item
        name = item['name']
        url = request.url
        image_name = hashlib.sha1(request.url.encode('utf-8')).hexdigest()
        image_ext = os.path.splitext(url)[1]
        return f'full/{name}/{image_name}{image_ext}'




