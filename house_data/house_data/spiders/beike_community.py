# -*- coding: utf-8 -*-
import scrapy
import pymongo
from ..item.community import Community

COMMUNITY_URL = 'https://{0}.ke.com/xiaoqu/{1}/'

class BeikeCommunitySpider(scrapy.Spider):
    name = 'beike_community'
    allowed_domains = ['ke.com']

    def __init__(self, cities='bj', *args, **kwargs):
        super(BeikeCommunitySpider, self).__init__()
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
            self.logger.info('请求{0}{1}{2}的小区'.format(r['city'], r['district'], r['name']))
            yield scrapy.Request(
                url = COMMUNITY_URL.format(r['city_code'], r['code']),
                callback = self.parse_communities,
                meta = {
                    'city': r['city'],
                    'district': r['district'],
                    'region': r['name'],
                    'city_code': r['city_code'],
                    'region_code': r['code']
                }
            )
        
    def parse_communities(self, response):
        content = response.xpath('//div[@class="content"]')[0]
        total = int(content.xpath('.//h2[contains(@class, "total")]/span/text()').get())
        
        city = response.meta['city']
        district = response.meta['district']
        region = response.meta['region']
        city_code = response.meta['city_code']
        
        
        if total == 0:
            self.logger.info('{0}{1}{2}没有小区, 网址为:{3}'.format(city, district, region, response.url))
            return None
        
        
        self.logger.info('{0}{1}{2}小区总数为:{3}'.format(city, district, region, total))
        
        return self.crawl_communities_in_page(1, region, district, city, response.url, city_code, total)
        
    def crawl_communities_in_page(self, page, region, district, city, prefix, city_code, total):
        
        url = prefix + 'pg' + str(page)
        
        self.logger.info('爬取{0}{1}{2}小区第{3}页, 包括此页还剩{4}个'.format(city, district, region, page, total))
        
        return scrapy.Request(
            url = url,
            callback = self.parse_communities_in_page,
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
    
    def parse_communities_in_page(self, response):
        district = response.meta['district']
        city = response.meta['city']
        region = response.meta['region']
        
        total = response.meta['total']
        page = response.meta['page']
        prefix = response.meta['prefix']
        city_code = response.meta['city_code']
        
        
        content = response.xpath('//div[@class="content"]')[0]
        ul = content.xpath('.//ul[@class="listContent"]//li')
        
        for li in ul:
            tags = li.xpath('.//div[@class="tagList"]/span//text()').extract()
            detail_url = li.xpath('./a/@href').get()
            _id = li.xpath('.//@data-housecode').get()

            community = Community()
            community['_id'] = _id
            community['tags'] = tags
            community['city'] = city
            community['district'] = district
            community['region'] = region
            community['link'] = detail_url
            yield scrapy.Request(
                url = detail_url,
                callback = self.parse_community,
                meta = {
                    'community': community
                }
            )
        
        total -= len(ul)
        
        self.logger.info('{0}{1}{2}小区第{3}页共有{4}个小区, 总共还剩{5}个小区'.format(city, district, region, page, len(ul), total))
        
        if total > 0 and len(ul) > 0:
            yield self.crawl_communities_in_page(page + 1, region, district, city, prefix, city_code, total)
            
    def parse_community(self, response):
        def has_value(list_value): 
            return list_value and len(list_value) >= 1

        detail_page = response.xpath('//div[@class="xiaoquDetailPage"]')[0]
        title = detail_page.xpath('.//div[@data-component="detailHeader"]//div[@class ="title"]/h1/text()').get().strip()

        community = response.meta['community']
        community_desc = detail_page.xpath('.//div[contains(@class, "xiaoquDescribe")]')[0]

        node = community_desc.xpath('.//span[text() = "物业费用"]//following::span[1]//text()')
        if has_value(node):
            real_estate_price = node.get().strip()
            community['real_estate_price'] = real_estate_price
            
        node = community_desc.xpath('.//span[text() = "物业公司"]//following::span[1]//text()')
        if has_value(node):
            real_estate = node.get().strip()
            community['real_estate'] = real_estate
            
        node = community_desc.xpath('.//span[@class="xiaoquUnitPrice"]//text()')
        if has_value(node):
            avg_unit_price = node.get().strip()
            community['avg_unit_price'] = avg_unit_price
        
        community['name'] = title
        return community