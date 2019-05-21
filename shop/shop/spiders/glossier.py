# -*- coding: utf-8 -*-
import scrapy

from shop.items import ShopItem
from selenium import webdriver

from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
import json
import logging

logger = logging.getLogger(__name__)

class GlossierSpider(scrapy.Spider):
    name = 'glossier'
    allowed_domains = ['glossier.com']
    # start_urls = ['https://www.glossier.com/products']
    start_urls = ['https://www.glossier.com/api/catalogs?version=1558350075']

    def __init__(self):
        # self.browser = webdriver.PhantomJS()
        # self.browser = None
        super(GlossierSpider, self).__init__()
        dispatcher.connect(self.spiderClosed, signals.spider_closed)

    def parse(self, response):
        text = response.body.decode(response.encoding)
        body =  json.loads(text)
        categories = body['catalogs']

        for cate in categories:
            name = cate['master']['name']
            price = cate['master']['price']
            link = 'https//www.glossier.com/products/' + cate['variants'][0]['slug']
            item = ShopItem()
            item['name'] = name
            item['link'] = link
            item['price'] = price
            yield item

            # for v in cate['variants']:

            #     name = v['name']
            #     price = v['price']
            #     link = 'https://www.glossier.com/products/' + v['slug']
            #     item = ShopItem()
            #     item['name'] = name
            #     item['link'] = link
            #     item['price'] = price
            #     items.append(item)

        # return items

    def spiderClosed(self, spider):
        # self.browser.quit()
        pass
