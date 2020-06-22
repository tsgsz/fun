# -*- coding: utf-8 -*-
import scrapy
import pymongo
from ..item.real_estate import RealEstate

REAL_ESTATE_URL = 'https://{0}.fang.ke.com/loupan/{1}/'

class BeikeRealEstateSpider(scrapy.Spider):
    name = 'beike_real_estate'
    allowed_domains = ['ke.com']
    
    def __init__(self, cities='bj', *args, **kwargs):
        super(BeikeRealEstateSpider, self).__init__()
        self.cities = cities.split(',')


    def start_requests(self):
        client = pymongo.MongoClient(self.settings['MONGO_DB_URL'])
        db = client['house_data']
        region = db['Region']
        regions = region.find(
            {'$or': [{'city_code': city} for city in self.cities]}, 
            {'_id': 0, 'code': 1, 'district': 1, 'city': 1, 'city_code': 1, 'name': 1}
        )
        for r in regions:
            yield scrapy.Request(
                url = REAL_ESTATE_URL.format(r['city_code'], r['code']),
                callback = self.parse_real_estates,
                meta = {
                    'city': r['city'],
                    'district': r['district'],
                    'region': r['name'],
                    'city_code': r['city_code'],
                    'region_code': r['code']
                }
            )
        
    def parse_real_estates(self, response):
        total = int(response.xpath('//span[text()="为您找到"]/../span[@class="value"]/text()').get())
        city = response.meta['city']
        district = response.meta['district']
        region = response.meta['region']
        city_code = response.meta['city_code']
        
        
        if total == 0:
            self.logger.info('{0}{1}{2}没有新楼盘, 网址为:{3}'.format(city, district, region, response.url))
            return None
        
        
        self.logger.info('{0}{1}{2}新楼盘总数为:{3}'.format(city, district, region, total))
        
        return self.crawl_real_estates_in_page(1, region, district, city, response.url, city_code, total)
        
    def crawl_real_estates_in_page(self, page, region, district, city, prefix, city_code, total):
        
        url = prefix + 'pg' + str(page)
        
        self.logger.info('爬取{0}{1}{2}楼盘第{3}页, 包括此页还剩{4}个'.format(city, district, region, page, total))
        
        return scrapy.Request(
            url = url,
            callback = self.parse_real_estates_in_page,
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
    
    def parse_real_estates_in_page(self, response):
        district = response.meta['district']
        city = response.meta['city']
        region = response.meta['region']
        
        total = response.meta['total']
        page = response.meta['page']
        prefix = response.meta['prefix']
        city_code = response.meta['city_code']
        
        
        end_flag = response.xpath('//ul[@class="resblock-list-wrapper"]/li[text()="猜你喜欢"]')
        
        
        if len(end_flag) == 0:
            ul = response.xpath('//ul[@class="resblock-list-wrapper"]/li')
        else:
            ul = end_flag.xpath('./preceding-sibling::li')
        
        for li in ul:
            tags = li.xpath('.//div[@class="resblock-tag"]/span/text()').extract()
            detail_url = 'https://{0}.fang.ke.com'.format(city_code) + li.xpath('a/@href').get()
            unit_node = li.xpath('.//div[@class="main-price"]/span[contains(., "均价")]')
            
            name = li.xpath('.//div[@class="resblock-name"]//@title').get() 
            
            _id = li.xpath('.//@data-project-name').get()
            has_avg_price = len(unit_node) != 0
            real_estate = RealEstate()
            real_estate['_id'] = _id

            real_estate['tags'] = tags
            real_estate['city'] = city
            real_estate['district'] = district
            real_estate['region'] = region
            real_estate['link'] = detail_url
            real_estate['name'] = name
            
            if has_avg_price:
                real_estate['avg_unit_price'] = unit_node.xpath('./preceding-sibling::span/text()').get().strip()
            
            yield scrapy.Request(
                url = detail_url,
                callback = self.parse_real_estate,
                meta = {
                    'real_estate': real_estate
                }
            )
        
        
        total -= len(ul)
        
        self.logger.info('{0}{1}{2}楼盘第{3}页共有{4}个新楼盘, 总共还剩{5}个新楼盘'.format(city, district, region, page, len(ul), total))
        
        if total > 0:
            yield self.crawl_real_estates_in_page(page + 1, region, district, city, prefix, city_code, total)
            
    def parse_real_estate(self, response):
        real_estate = response.meta['real_estate']
        real_estate['open_date'] = response.xpath('//div[@class="open-date"]/span[@class="content"]/text()').get()
        return scrapy.Request(
            url = real_estate['link'] + 'xiangqing',
            callback = self.parse_real_estate_detail,
            meta = {
                'real_estate': real_estate
            }
        )
    
    def parse_real_estate_detail(self, response):
        real_estate = response.meta['real_estate']
        infos = response.xpath('//ul[@class="x-box"]/li')
        
        def get_val(name):
            label = infos.xpath('./span[contains(., "{0}")]/../span[@class="label-val"]'.format(name))
            x = label.xpath('./text()').get()
            if x is None or len(x.strip()) == 0:
                x = label.xpath('./span/text()').get()    
            return x.strip() if x else ''
        
        avg_unit_price = get_val('参考价格')

        if avg_unit_price and avg_unit_price.find("均价") != -1:
            real_estate['avg_unit_price'] = avg_unit_price.replace(u'均价', '').replace(u'元/平', '').strip()
            
        real_estate['real_estate'] = get_val('物业公司')
        
        p = get_val('物业费')
        if p:
            real_estate['real_estate_price'] = p.replace('元/m²/月', '')
            
        real_estate['estate_type'] = get_val('物业类型')
        real_estate['building_type'] = get_val('建筑类型')
        real_estate['floor_area'] = get_val('占地面积').replace('㎡', '')
        real_estate['floor_space'] = get_val('建筑面积').replace('㎡', '')
        real_estate['house_num'] = get_val('规划户数')
        real_estate['property_right_years'] = get_val('产权年限')
        real_estate['latest_transfer'] = get_val('最近交房')
        real_estate['greening_rate'] = get_val('绿化率')
        real_estate['floor_area_rate'] = get_val('容积率')
        real_estate['parking_place_ratio'] = get_val('车位配比')
        real_estate['heating'] = get_val('供暖方式')
        real_estate['water'] = get_val('供水')
        real_estate['electricity'] = get_val('供电')
        return scrapy.Request(
            url = real_estate['link'] + 'huxingtu',
            callback = self.parse_real_estate_layouts,
            meta = {
                'real_estate': real_estate
            }
        )
    def parse_real_estate_layouts(self, response):
        real_estate = response.meta['real_estate']
        real_estate['layouts'] = list()
        layouts = response.xpath('//ul[contains(@class, "item-list")]/li')
        for li in layouts:
            layout = dict()
            info = li.xpath('.//ul/li/text()').extract()
            for i in info:
                kv = i.split('：')
                if kv[0].strip() == '建面':
                    layout['building_size'] = kv[1].strip().replace('㎡', '')
                elif kv[0].strip() == '居室':
                    layout['layout'] = kv[1].strip()
                
            
            layout['avg_total_price'] = li.xpath('.//i/text()').get()
            real_estate['layouts'].append(layout)
            
        return real_estate