import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from spiders.pharma_intelligence import PharmaIntelligenceSpider

#while True:
process =  CrawlerProcess(settings=get_project_settings())
process.crawl(PharmaIntelligenceSpider)

process.start()
