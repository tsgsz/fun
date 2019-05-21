# -*- coding: utf-8 -*-
import scrapy

from shop.items import ShopItem
from selenium import webdriver

from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
import json
import logging
import re

logger = logging.getLogger(__name__)

class ColourpopSpider(scrapy.Spider):
    name = 'colourpop'
    allowed_domains = ['colourpop.com']
    # start_urls = ['https://www.glossier.com/products']
    start_urls = ['https://colourpop.com/collections/best-sellers?sort_by=default&view=__DO-NOT-SELECT__.products&page=1']

    def __init__(self):
        # self.browser = webdriver.PhantomJS()
        self.browser = None
        super(ColourpopSpider, self).__init__()
        dispatcher.connect(self.spiderClosed, signals.spider_closed)

    def parse(self, response):
        # api = 'https://www.glossier.com/api/catalogs?version=1558350075'
        # yield scrapy.Request(url = api, callback = self.parseCatalogs)
        # context = response.xpath('//*[@id="main"]/div[2]/div/div/div[2]')

        # for i, div in enumerate(context):
        #     if i % 2 == 1:
        #         for li in div.xpath('ul'):
        #             item = ShopItem()
        #             name_text = li.xpath('div/div[3]/a[1]/p[1]/@text()').extract()[0]
        #             price_text = li.xpath('div/div[3]/a[2]/@text()')[0]
        #             price_idx = price_text.find('$')
        #             price = price_text[price_idx:]
        #             herf = li.xpath('div/div[3]/a[2]/@herf()')[0]
        #             item['name'] = name_text
        #             item['price'] = price
        #             item['link'] = herf
        #             items.append(item)

        # open("xxx.html","w").write(response.body).close()
        # text = response.body.xpath('html/body/pre/@text()').extract()[0]
        # text = str(response.body).decode('utf-8').replace("'", '"').strip('()')
        text = response.body.decode(response.encoding)
        # open("self.json","wb").write(response.body).close()
        body =  json.loads(text)
        # open("self.json","wb").write(json.dumps(body, indent=4).encode('utf-8')).close()

        pages = body['pages']
        page = body['page']

        if page <= pages:
            payload = body['payload']

            for p in payload:
                item = ShopItem()
                item['name'] = p['title']
                item['link'] = 'https://www.colourpop.com/' + p['url']

                price = p['price_html']
                reg_pattern='(<[^<>]*>)+([^<>]*?)(<[^<>]*>)+'
                price = re.sub(reg_pattern, '', price)
                price_idx = price.find('$')
                item['price'] = price[price_idx + 1:]

                yield item
            if page + 1 <= pages:
                next_url = 'https://colourpop.com/collections/best-sellers?sort_by=default&view=__DO-NOT-SELECT__.products&page=' + (page + 1)
                yield scrapy.Request(next_url, self.parse)

    def spiderClosed(self, spider):
        self.browser.quit()
        pass
