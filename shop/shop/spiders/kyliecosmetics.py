# -*- coding: utf-8 -*-
import scrapy

from shop.items import ShopItem
from selenium import webdriver

from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
import json
import logging

logger = logging.getLogger(__name__)

class KyliecosmeticsSpider(scrapy.Spider):
    name = 'kyliecosmetics'
    allowed_domains = ['kyliecosmetics.com']
    # start_urls = ['https://www.glossier.com/products']
    # start_urls = ['https://colourpop.com/collections/best-sellers?sort_by=default&view=__DO-NOT-SELECT__.products&page=1']
    start_urls = ['https://www.kyliecosmetics.com/collections/best-sellers']

    def __init__(self):
        # self.browser = webdriver.PhantomJS()
        # self.browser = None
        super(KyliecosmeticsSpider, self).__init__()
        dispatcher.connect(self.spiderClosed, signals.spider_closed)

    def parse(self, response):

        products = response.xpath('//*[@class="product-contents"]')

        for p in products:
            item = ShopItem()
            logger.debug(p.xpath('a[@class="product-title"]/@href').extract())
            name = p.xpath('a[@class="product-title"]/text()').extract()[0]
            herf = p.xpath('a[@class="product-title"]/@href').extract()[0]
            price_path = p.xpath('div[@class="product-price"]')
            if price_path.xpath('div[@class="onsale"]'):
                price_path = price_path.xpath('div[@class="onsale"]')

            price_text = price_path.xpath('./text()').extract()[0]
            price_idx = price_text.find('$')
            price = price_text[price_idx + 1:]
            item['name'] = name.strip().strip('\n').strip()
            item['price'] = price.strip()
            item['link'] = 'https://www.kyliecosmetics.com/' + herf.strip()
            yield item

        # open("xxx.html","w").write(response.body).close()
        # text = response.body.xpath('html/body/pre/@text()').extract()[0]
        # text = str(response.body).decode('utf-8').replace("'", '"').strip('()')

    def spiderClosed(self, spider):
        # self.browser.quit()
        pass
