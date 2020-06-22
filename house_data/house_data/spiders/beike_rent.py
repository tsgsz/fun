# -*- coding: utf-8 -*-
import scrapy
import pymongo
from ..item.rent import Rent
from ..utils import *

RENT_URL = 'https://{0}.zu.ke.com/zufang/rs{1}/'
RENT_PAGE_URL = 'https://{0}.zu.ke.com/zufang/pg{2}/rs{1}' 

class BeikeRentSpider(scrapy.Spider):
    name = 'beike_rent'
    allowed_domains = ['ke.com']
    
    def __init__(self, cities='bj', *args, **kwargs):
        super(BeikeRentSpider, self).__init__()
        self.cities = cities.split(',')

    def start_requests(self):
        client = pymongo.MongoClient(self.settings['MONGO_DB_URL'])
        db = client['house_data']
        community_db = db['Community']
        communities = community_db.find(
            {'$or': [{'city': city_code_to_city(city)} for city in self.cities]}, 
            {'_id': 0, 'name': 1, 'city': 1}
        )
        for c in communities:
            self.logger.info('请求{0}{1}的租房信息'.format(c['city'], c['name']))
            yield scrapy.Request(
                url = RENT_URL.format(city_to_city_code(c['city']), c['name']),
                callback = self.parse_rents,
                meta = {
                    'city_code': city_to_city_code(c['city']),
                    'community': c['name'],
                    'city': c['city']
                }
            )
            
    def parse_rents(self, response):
        meta = response.meta
        city = meta['city']
        city_code = meta['city_code']
        community = meta['community']
        total = int(response.xpath('//p[contains(., "为您找到")]/span/text()').get())
        if total == 0:
            self.logger.info('{0}{1}没有房子出租, 网址为:{2}'.format(city, community, response.url))
            return None
        
        self.logger.info('{0}{1}出租屋总数为:{2}'.format(city, community, total))
        return self.crawl_rents_in_page(1, city_code, community, total)
    
    
    def crawl_rents_in_page(self, page, city_code, community, total):
        url = RENT_PAGE_URL.format(city_code, community, page)
        self.logger.info('爬取{0}租房第{1}页, 包括此页还剩{2}个'.format(community, page, total))
        return scrapy.Request(
            url = url,
            callback = self.parse_rents_in_page,
            meta = {
                'city_code': city_code,
                'community': community,
                'page': page,
                'total': total
            }
        )
    
    def parse_rents_in_page(self, response):
        total = response.meta['total']
        page = response.meta['page']
        community = response.meta['community']
        city_code = response.meta['city_code']
        
        ul = response.xpath('//div[@class="content__list"]/div[@class="content__list--item"]')
        
        self.logger.info('{0}小区第{1}页共有{2}个租房, 总共还剩{3}个租房'.format(community, page, len(ul), total-len(ul)))
        
        for li in ul:
            rent = Rent()
            rent['name'] = li.xpath('.//p[contains(@class, "content__list--item--title")]/a/text()').get().strip()
            rent['community'] = community
            rent['link'] =  'https://{0}.zu.ke.com{1}'.format(city_code, li.xpath('.//@href').get())
            rent['tags'] = li.xpath('.//p[contains(@class, "content__list--item--bottom")]/i/text()').extract()
            rent['_id'] = li.xpath('.//@data-house_code').get()
            yield scrapy.Request(
                url = rent['link'],
                callback = self.parse_rent,
                meta = {
                    'rent': rent
                }
            )
            
        total -= len(ul)
        if total > 0 and len(ul) > 0:
            yield self.crawl_rents_in_page(page + 1, city_code, community, total)
            

    
    def parse_rent(self, response):
        rent = response.meta['rent']
        
        rent['rent_type'] = response.xpath('//span[contains(., "租赁方式")]/../text()').get()
        
        def get_val(key):
            return response.xpath('//li[contains(., "{0}")]/text()'.format(key)).get().split('：')[-1]
        
        rent['size'] = get_val('面积').replace('㎡', '')
        rent['maintains'] = get_val('维护')
        rent['level'] = response.xpath('//li[contains(., "{0}") and @class != "label"]/text()'.format('楼层')).get().split('：')[-1]
        rent['parking_place'] = get_val('车位')
        rent['electricity'] = get_val('用电')
        rent['heating'] = get_val('采暖')
        rent['lease_term'] = get_val('租期')
        rent['check_house'] = get_val('看房')
        rent['orientation'] = get_val('朝向：')
        rent['check_in_date'] = get_val('入住')
        rent['elevator'] = get_val('电梯')
        rent['water'] = get_val('用水')
        rent['gas'] = get_val('燃气')
        
        rent['pay'] = list()
        
        def get_pay(node):
            pay = dict()
            ul = node.xpath('./li/text()').extract()
            pay['payment_type'] = ul[0]
            pay['total_price'] = ul[1]
            pay['margin'] = ul[2]
            pay['tips'] = ul[3]
            pay['commission'] = ul[4]
            
            return pay
        
        cost_tables = response.xpath('//div[contains(@data-el, "costEl")]//ul[@class="table_row"]')
        
        for table in cost_tables:
            pay = get_pay(table)
            rent['pay'].append(pay)
            
        return rent    