# -*- coding: utf-8 -*-
import scrapy
import pymongo
from ..item.deal import Deal
from ..utils import *

DEAL_URL = 'https://{0}.ke.com/chengjiao/pg{2}rs{1}/'

class BeikeDealSpider(scrapy.Spider):
    name = 'beike_deal'
    allowed_domains = ['ke.com']
    
    def __init__(self, cities='bj', *args, **kwargs):
        super(BeikeDealSpider, self).__init__()
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
            self.logger.info('请求{0}{1}的交易信息'.format(c['city'], c['name']))
            yield scrapy.Request(
                url = DEAL_URL.format(city_to_city_code(c['city']), c['name']),
                callback = self.parse_deals,
                meta = {
                    'city_code': city_to_city_code(c['city']),
                    'community': c['name'],
                    'city': c['city']
                }
            )
    
    def parse_deals(self, response):
        meta = response.meta
        city = meta['city']
        city_code = meta['city_code']
        community = meta['community']
        content = response.xpath('//div[@class="leftContent"]')[0]
        total = int(content.xpath('.//div[contains(@class, "total")]/span/text()').get())
        total = int(response.xpath('//p[contains(., "为您找到")]/span/text()').get())
        if total == 0:
            self.logger.info('{0}{1}没有房子成交, 网址为:{2}'.format(city, community, response.url))
            return None
        
        self.logger.info('{0}{1}成交总数为:{2}'.format(city, community, total))
        return self.crawl_deals_in_page(1, city_code, community, total)
    
    def crawl_deals_in_page(self, page, city_code, community, total):
        url = DEAL_PAGE_URL.format(city_code, community, page)
        self.logger.info('爬取{0}成交第{1}页, 包括此页还剩{2}个'.format(community, page, total))
        return scrapy.Request(
            url = url,
            callback = self.parse_deals_in_page,
            meta = {
                'city_code': city_code,
                'community': community,
                'page': page,
                'total': total
            }
        )
    
    def parse_deals_in_page(self, response):
        total = response.meta['total']
        page = response.meta['page']
        community = response.meta['community']
        city_code = response.meta['city_code']
        
        
        self.logger.info('{0}小区第{1}页共有{2}个成交记录, 总共还剩{3}个成交记录'.format(community, page, len(ul), total-len(ul)))
        content = response.xpath('//div[@class="leftContent"]')[0]
        ul = content.xpath('//ul[@class="listContent"]//li')
        
        for li in ul:
            tags = li.xpath('//div[@class="title"]/a/text()').get().strip()
            detail_url = li.xpath('a/@href').get()
            
            deal_date = li.xpath('//div[@class="dealDate"]/text()').get().strip()
            total_price = li.xpath('//div[@class="totalPrice"]/span/text()').get().replace('万', '').strip()
            price = li.xpath('//div[@class="unitPrice"]/span/text()').get().replace('元/平', '').strip()
            
            deal = Deal()
            
            deal['community'] = community['name']
            deal['link'] = detail_url
            deal['total_price'] = total_price
            deal['price'] = price
            deal['time'] = deal_date
            yield scrapy.Request(
                url = detail_url,
                callback = self.parse_deal,
                meta = {
                    'deal': deal
                }
            )
            
        total -= len(ul)
        if total > 0 and len(ul) > 0:
            yield self.crawl_deals_in_page(page + 1, city_code, community, total)
            
    def parse_deal(self, response):
        
        deal = response.meta['deal']
        
        msg = response.xpath('//div[@class="msg"]')
        
        if len(msg) > 0:
            msg = msg[0]
        
            try:
                
                def get_val(key):
                    return msg.xpath('span[contains(.,"{0}")]/label/text()'.format(key)).get().strip()
                
                deal['init_price'] = get_val('挂牌价格')
                deal['deal_cycle'] = get_val('成交周期')
        
                deal['price_adjustment'] = get_val('调价')
                deal['check_times'] = get_val('带看')
                deal['stars'] = get_val('关注')
                deal['glance_over'] = get_val('浏览')
            except Exception as e:
                self.logger.warning('info panel not complete %s', e)
            
        
        base = response.xpath('//div[@class="base"]')[0]
        
                    
        def get_val(node, key):
            return node.xpath('.//span[contains(.,"{0}")]/../text()'.format(key)).get().strip()
        
        deal['layout'] = get_val(base, '房屋户型')
        deal['building_size'] = get_val(base, '建筑面积').replace('㎡', '')
        deal['actual_size'] = get_val(base, '套内面积').replace('㎡', '')
        level_str = get_val(base, '所在楼层')
        
        deal['level'] = re.findall('(.*)楼层', level_str)
        deal['total_level'] = re.findall('共(.*)层', level_str)
        
        deal['orientation'] = get_val(base, '房屋朝向')
        
        try:
            deal['usage'] = float(actual_size) / float(building_size)
        except:
            self.logger.info('房源 %s 的 面积有问题',deal['link'])

            
        deal['layout_structure'] = get_val(base, '户型结构')
        
        deal['building_type'] = get_val(base, '建筑类型')
        deal['building_structure'] = get_val(base, '建筑结构')
        deal['construct_year'] = get_val(base, '建成年代')
        deal['echelon_ratio'] = get_val(base, '梯户比例')
        
        deal['has_elevator'] = get_val(base, '配备电梯')

        deal['decoration'] = get_val(base, '装修情况')
        
        deal['heating'] = get_val(base, '供暖方式')
        
        transaction = response.xpath('//div[@class="transaction"]')[0]
        
        deal['_id'] = get_val(transaction, '链家编号')
        deal['deal_class'] = get_val(transaction, '交易权属')
        deal['init_time'] =  get_val(transaction, '挂牌时间')
        deal['house_age'] =  get_val(transaction, '房屋年限')
        deal['house_usage'] = get_val(transaction, '房屋用途')
        deal['house_ownership'] =  get_val(transaction, '房权所属')
        
        deal['tags'] = response.xpath('//div[text()="房源标签"]/../div/a/text()').extract()
        
        return deal