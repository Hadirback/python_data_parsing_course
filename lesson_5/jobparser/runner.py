from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from jobparser import settings
from jobparser.spiders.hhru import HhruSpider
# from jobparser.spiders.hhru import SPruSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    # answers = input()
    process.crawl(HhruSpider, vacancy='python')
    #process.crawl(SPruSpider, vacancy='python')
    process.start()