# -*- coding: utf-8 -*-
import scrapy
import pymongo
from ..item.second_house import SecondHouse

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import re

HOUSE_URL = 'https://{0}.ke.com/ershoufang/{1}/'

class Beike2ndHouseSpider(scrapy.Spider):
    name = 'beike_2nd_house'
    allowed_domains = ['ke.com']

    def __init__(self, cities='bj', *args, **kwargs):
        super(Beike2ndHouseSpider, self).__init__()
        self.cities = cities.split(',')
        
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("window-size=1024,768")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("–incognito")

        self.browser = webdriver.Chrome(r'/usr/local/bin/chromedriver', chrome_options=chrome_options)
    
    def close(self,spider):
        self.browser.quit()

    def start_requests(self):
        client = pymongo.MongoClient(self.settings['MONGO_DB_URL'])
        db = client['house_data']
        region = db['Region']
        regions = region.find(
            {'$or': [{'city_code': city} for city in self.cities]}, 
            {'_id': 0, 'code': 1, 'district': 1, 'city': 1, 'city_code': 1, 'name': 1}
        )
        for r in regions:
            self.logger.info('请求{0}{1}{2}的小区'.format(r['city'], r['district'], r['name']))
            yield scrapy.Request(
                url = HOUSE_URL.format(r['city_code'], r['code']),
                callback = self.parse_2nd_houses,
                meta = {
                    'city': r['city'],
                    'district': r['district'],
                    'region': r['name'],
                    'city_code': r['city_code'],
                    'region_code': r['code']
                }
            )
        
    def parse_2nd_houses(self, response):
        content = response.xpath('//div[@class="leftContent"]')[0]
        total = int(content.xpath('.//h2[contains(@class, "total")]/span/text()').get())
        
        city = response.meta['city']
        district = response.meta['district']
        region = response.meta['region']
        city_code = response.meta['city_code']
        
        
        if total == 0:
            self.logger.info('{0}{1}{2}没有二手房, 网址为:{3}'.format(city, district, region, response.url))
            return None
        
        
        self.logger.info('{0}{1}{2}二手房为:{3}'.format(city, district, region, total))
        
        return self.crawl_2nd_houses_in_page(1, region, district, city, response.url, city_code, total)
        
    def crawl_2nd_houses_in_page(self, page, region, district, city, prefix, city_code, total):
        
        url = prefix + 'pg' + str(page)
        
        self.logger.info('爬取{0}{1}{2}二手房第{3}页, 包括此页还剩{4}个'.format(city, district, region, page, total))
        
        return scrapy.Request(
            url = url,
            callback = self.parse_2nd_houses_in_page,
            meta = {
                'city': city,
                'district': district,
                'region': region,
                'total': total,
                'page': page,
                'prefix': prefix,
                'city_code': city_code
            }
        )
    
    def parse_2nd_houses_in_page(self, response):
        district = response.meta['district']
        city = response.meta['city']
        region = response.meta['region']
        
        total = response.meta['total']
        page = response.meta['page']
        prefix = response.meta['prefix']
        city_code = response.meta['city_code']
        
        
        content = response.xpath('//div[@class="leftContent"]')[0]
        ul = content.xpath('.//ul[@class="sellListContent"]//li[@class="clear"]')
        
        for li in ul:
            tags = li.xpath('.//div[@class="tag"]/span//text()').extract()
            detail_url = li.xpath('./a/@href').get()
            community = li.xpath('.//div[@class="positionInfo"]/a//text()').get()

            house = SecondHouse()
            house['tags'] = tags
            house['community'] = community
            house['link'] = detail_url
            yield scrapy.Request(
                url = detail_url,
                callback = self.parse_2nd_house,
                meta = {
                    'house': house
                }
            )
        
        total -= len(ul)
        
        self.logger.info('{0}{1}{2}小区第{3}页共有{4}个二手房, 总共还剩{5}个二手房'.format(city, district, region, page, len(ul), total))
        
        if total > 0 and len(ul) > 0:
            yield self.crawl_2nd_houses_in_page(page + 1, region, district, city, prefix, city_code, total)
            
    
    def parse_2nd_house(self, response):
        
        house = response.meta['house']
        
        house['stars'] = response.xpath('//span[@id="favCount"]//text()').get()
        house['total_price'] = response.xpath('//div[@class="price "]/span/text()').get()
        house['price'] = response.xpath('//div[@class="unitPrice"]/span/text()').get()
        house['_id'] = response.xpath('//div[@class="houseRecord"]/span[@class="info"]/text()').get().strip()

        
        
        msg = response.xpath('//div[@class="msg"]')

        
        house['week_check_times'] = response.xpath('//div[@data-component="seeRecord"]//div[@class="count"]/text()').get().strip()
        house['month_check_times'] = response.xpath('//div[@data-component="seeRecord"]//div[@class="totalCount"]/span/text()').get().strip()
        
        base = response.xpath('//div[@data-component="baseinfo"]')[0]
        
                    
        def get_val(node, key):
            x = node.xpath('.//span[contains(.,"{0}")]/../text()'.format(key)).get()
            return x.strip() if x is not None else ''
                    
        house['layout'] = get_val(base, '房屋户型')
        house['building_size'] = get_val(base, '建筑面积').replace('㎡', '')
        house['actual_size'] = get_val(base, '套内面积').replace('㎡', '')
        level_str = get_val(base, '所在楼层')
        
        house['level'] = re.findall('(.*)楼层', level_str)
        house['total_level'] = re.findall('共(.*)层', level_str)
        
        house['orientation'] = get_val(base, '房屋朝向')
        
        try:
            house['usage'] = float(actual_size) / float(building_size)
        except:
            self.logger.info('房源 %s 的 面积有问题',house['link'])

            
        house['layout_structure'] = get_val(base, '户型结构')
        
        house['building_type'] = get_val(base, '建筑类型')
        house['building_structure'] = get_val(base, '建筑结构')
        house['construct_year'] = get_val(base, '建成年代')
        house['echelon_ratio'] = get_val(base, '梯户比例')
        
        house['has_elevator'] = get_val(base, '配备电梯')

        house['decoration'] = get_val(base, '装修情况')
        
        house['heating'] = get_val(base, '供暖方式')
                
        house['deal_class'] = get_val(base, '交易权属')
        house['init_time'] =  get_val(base, '挂牌时间')
        house['house_age'] =  get_val(base, '房屋年限')
        house['house_usage'] = get_val(base, '房屋用途')
        house['house_ownership'] =  get_val(base, '产权所属')
        house['house_certificate_copy'] = get_val(base, '房本备件')
        house['plege_info'] = get_val(base, '抵押信息')
        house['last_trade_time'] =  get_val(base, '上次交易')


        
        return house