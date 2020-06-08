# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem

class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['http://hh.ru/']

    #def __init__(self, vacancy):
        #self.start_urls = [f'строка запроса{vacancy}']

    def parse(self, response:HtmlResponse):
        next_page = response.css('a.HH-Pager-Controls-Next::attr(href)').extract_first()
        job_links = response.xpath("//a[@class='bloko-link HH-LinkModifier']/@href").extract()

        for link in job_links:
            yield response.follow(link, callback=self.vacancy_parse)

        yield response.follow(next_page, callback=self.parse)


    def vacancy_parse(self, response:HtmlResponse):
        name = response.xpath("//h1/text()").extract_first()
        salary = response.xpath("//p[@class='vacancy-salary']/span/text()").extract()
        yield JobparserItem(name=name, salary=salary)
        print(name, salary)