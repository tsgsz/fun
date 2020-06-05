# -*- coding: utf-8 -*-
import scrapy
import json as j
import re

from ..item.community import Community
from ..item.deal import Deal
from ..item.real_estate import RealEstate
from ..item.rent import Rent


DISTRICT_region_XPATH = '//div[3]/div[1]/dl[2]/dd/div/div[2]/a'
CITY_DISTRICT_XPATH = '///div[3]/div[1]/dl[2]/dd/div/div/a'

BAIDU_SEARCH = 'http://api.map.baidu.com/place/v2/search?query={0}&ttag=住宅&region={1}&output=json&ak=MQMeFXHTVvCx0hffjXCTj7mrqKhMnpTH&city_limit=true&page_size=1'
BAIDU_POI = 'http://api.map.baidu.com/place/v2/search?query="{0}"&location={1},{2}&radius=2000&output=json&ak=MQMeFXHTVvCx0hffjXCTj7mrqKhMnpTH&scope=2&page_size=10&radius_limit=true&page_num={3}'

CITY_DICT = {
    'bj': '北京',
    'cd': '成都',
    'cq': '重庆',
    'cs': '长沙',
    'dg': '东莞',
    'dl': '大连',
    'fs': '佛山',
    'gz': '广州',
    'hz': '杭州',
    'hf': '合肥',
    'jn': '济南',
    'nj': '南京',
    'qd': '青岛',
    'sh': '上海',
    'sz': '深圳',
    'su': '苏州',
    'sy': '沈阳',
    'tj': '天津',
    'wh': '武汉',
    'xm': '厦门',
    'yt': '烟台',
}

class BeikeSpider(scrapy.Spider):
    name = 'beike'
    allowed_domains = ['ke.com', 'baidu.com']

    chinese_district_dict = dict()     # 城市代码和中文名映射
    chinese_region_dict = dict()       # 版块代码和中文名映射
    chinese_region_dict = dict()


    def __init__(self, cities='bj', *args, **kwargs):
        super(BeikeSpider, self).__init__()
        self.cities = cities.split(',')
        self.start_urls = ['https://{0}.ke.com'.format(self.cities[0])]

    def parse(self, response):
        #暂时不需要登录

        for city in self.cities:
            yield self.crawl_districts_of_city(city)

    def crawl_districts_of_city(self, city):
        district_url = 'https://{0}.ke.com/xiaoqu'.format(city)
        return scrapy.Request(
            url = district_url,
            callback = self.parse_districts,
            meta = {
                'city': city
            }
        )
        

    def parse_districts(self, response):
        context = response.xpath(CITY_DISTRICT_XPATH)
        en_names = list()
        ch_names = list()
        city = response.meta['city']
        for ele in context:
            link = ele.attrib['href']
            en_names.append(link.split('/')[-2])
            ch_names.append(ele.xpath('.//text()')[0])

        for i, name in enumerate(en_names):
            self.chinese_district_dict[name] = ch_names[i]
            yield self.crawl_regions_in_district(name, city)



    def crawl_regions_in_district(self, district, city):
        region_url = 'https://{0}.ke.com/xiaoqu/{1}'.format(city, district)
        return scrapy.Request(
            url = region_url,
            callback = self.parse_regions,
            meta = {
                'city': city,
                'district': district
            }
        )

    def parse_regions(self, response):
        context = response.xpath(DISTRICT_region_XPATH)
        district = response.meta['district']
        city = response.meta['city']
        for link in context:
            relative_link = link.attrib['href']
            relative_link = relative_link[:-1]
            region = relative_link.split("/")[-1]
            if region != district:
                chinese_region = link.extract()
                self.chinese_region_dict[region] = chinese_region
                yield self.crawl_communities_in_region(region, district, city)
                yield self.crawl_real_estates_in_region(region, district, city)
                
    def crawl_real_estates_in_region(self, region, district, city):
        real_estates_url = 'https://{0}.ke.fang.com/loupan/{1}/'.format(city, region)
        return scrapy.Request(
            url = real_estates_url,
            callback = self.parse_real_estates,
            meta = {
                'city': city,
                'district': district,
                'region': region
            }
        )
        
                

    def crawl_communities_in_region(self, region, district, city):
        # self.logger.info('爬取 region: %s', region)
        communities_url = 'https://{0}.ke.com/xiaoqu/{1}/'.format(city, region)
        return scrapy.Request(
            url = communities_url,
            callback = self.parse_communities,
            meta = {
                'city': city,
                'district': district,
                'region': region
            }
        )

    def parse_communities(self, response):
        content = response.xpath('//div[@class="content"]')[0]

        total = int(content.xpath('.//h2[contains(@class, "total")]/span/text()').get())

        
        if total == 0:
            return None

        # yield self.parse_communities_in_page(response)

        district = response.meta['district']
        city = response.meta['city']
        region = response.meta['region']

        page_datas = content.xpath('.//@page-data')
        if len(page_datas) != 0:
            total_page = j.loads(page_datas.get())['totalPage']
            for i in range(1, total_page + 1):
                yield self.crawl_communities_in_page(i, region, district, city)
        else:
            yield self.parse_communities_in_page(response)
        

        
    def crawl_communities_in_page(self, page, region, district, city):
        # self.logger.info('爬取 region, page: %s %s', region, page)
        community_url = 'https://{0}.ke.com/xiaoqu/{1}/pg{2}'.format(city, region, page)
        return scrapy.Request(
            url = community_url,
            callback = self.parse_communities_in_page,
            meta = {
                'city': city,
                'district': district,
                'region': region
            }
        )

    def parse_communities_in_page(self, response):
        district = response.meta['district']
        city = response.meta['city']
        region = response.meta['region']
        content = response.xpath('//div[@class="content"]')[0]
        ul = content.xpath('.//ul[@class="listContent"]//li')
        for li in ul:
            tags = li.xpath('.//div[@class="tagList"]/span//text()').extract()
            detail_url = li.xpath('./a/@href').get()
            community_id = li.xpath('.//@data-housecode').get()

            community = Community()
            community['community_id'] = community_id
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

    def parse_real_estates(self, response):
        total = int(response.xpath('//span[text()="为您找到"]/../span[@class="value"]/text()').get())

        
        if total == 0:
            return None

        district = response.meta['district']
        city = response.meta['city']
        region = response.meta['region']

        return self.crawl_estates_in_page(1, region, district, city, total)

    def crawl_real_estates_in_page(self, page, region, district, city, total):
        # self.logger.info('爬取 region, page: %s %s', region, page)
        community_url = 'https://{0}.ke.com/xiaoqu/{1}/pg{2}'.format(city, region, page)
        return scrapy.Request(
            url = community_url,
            callback = self.parse_real_estates_in_page,
            meta = {
                'city': city,
                'district': district,
                'region': region,
                'total': total,
                'page': page
            }
        )

    def parse_real_estates_in_page(self, response):
        district = response.meta['district']
        city = response.meta['city']
        region = response.meta['region']
        
        total = response.meta['total']
        page = response.meta['page']
        
        
        end_flag = response.xpath('//ul[@class="resblock-list-wrapper"]/li[text()="猜你喜欢"]')
        
        if len(end_flag) == 0:
            ul = response.xpath('//ul[@class="resblock-list-wrapper"]/li')
        else:
            ul = end_flag.xpath('./preceding-sibling::li')
            
        for li in ul:
            tags = li.xpath('.//div[@class="resblock-tag"]/span/text()').extract()
            detail_url = 'http://{0}.fang.ke.com'.format(city) + li.xpath('a/@href').get()
            unit_node = li.xpath('.//div[@class="main-price"]/span[contains(., "均价")]')
            
            name = li.xpath('.//div[@class="resblock-name"]//@title').get() 

            
            has_avg_price = len(unit_node) != 0
            
            real_estate = RealEstate()

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
        
        if total > 0:
            return self.crawl_communities_in_page(page + 1, region, district, city, total)
        

    def has_value(self, list_value):
        return list_value and len(list_value) >= 1
    
    def parse_real_estate(self, response):
        real_estate = response.meta['real_estate']
        real_estate['open_date'] = response.xpath('//div[@class="open-date"]/span[@class="content"]/text()').get()
        return scrapy.Request(
            url = real_estate['link'] + '/xiangqing/',
            callback = self.parse_real_estate_detail,
            meta = {
                'real_estate': real_estate
            }
        )
    
    
    def parse_real_estate_detail(self, response):
        real_estate = response.meta['real_estate']
        
        infos = response.xpath('//ul[@class="x-box"]/li')
        
        def get_val(name):
            x = infos.xpath('./span[contains(., "{0}")]/../span[@class="label-val"]/span/text()'.format(name)).get()
            return x.strip() if x else ''
        
        avg_unit_price = get_val('参考价格')
        
        if avg_unit_price and avg_unit_price.find("均价") != -1:
            real_estate['avg_unit_price'] = p.replace(u'均价', '').replace(u'元/平', '').strip()
            
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
            url = real_estate['link'] + '/huxingtu',
            callback = self.parse_real_estate_layouts,
            meta = {
                'real_estate': real_estate
            }
        )
        
        
    def parse_layouts_estate(self, response):
        real_estate = response.meta['real_estate']
        
        real_estate['layouts'] = list()
        
        layouts = response.xpath('//ul[contains(@class, "item-list")]/li')
        for li in layouts:
            layout = dict()
            info = layout.xpath('.//ul/li/text()').extract()
            for i in info:
                kv = i.split(':')
                layout[kv[0].strip()] = kv[1].strip()
            
            layout['avg_total_price'] = li.xpath('.//i/text()').get()
            real_estate['layouts'].append(layout)
        
        yield scrapy.Request(
            url = search_url,
            callback = self.parse_location,
            meta = {
                'item': real_estate
            }
        )
        
        
    def parse_community(self, response):

        detail_page = response.xpath('//div[@class="xiaoquDetailPage"]')[0]
        title = detail_page.xpath('.//div[@data-component="detailHeader"]//div[@class ="title"]/h1/text()').get().strip()

        community = response.meta['community']

        community_desc = detail_page.xpath('.//div[contains(@class, "xiaoquDescribe")]')[0]

        node = community_desc.xpath('.//span[text() = "物业费用"]//following::span[1]//text()')
        if self.has_value(node):
            real_estate_price = node.get().strip()
            community['real_estate_price'] = real_estate_price
            
        node = community_desc.xpath('.//span[text() = "物业公司"]//following::span[1]//text()')
        if self.has_value(node):
            real_estate = node.get().strip()
            community['real_estate'] = real_estate
            
        node = community_desc.xpath('.//span[@class="xiaoquUnitPrice"]//text()')
        if self.has_value(node):
            avg_unit_price = node.get().strip()
            community['avg_unit_price'] = avg_unit_price
        
        community['name'] = title
        
        # self.logger.info('爬取 小区信息, %s', str(response.meta['community']))

        
        # 获取 POI 数据
        # 获取经纬度
        cn_city = CITY_DICT[response.meta['community']['city']]
        search_url = BAIDU_SEARCH.format(title, cn_city) 
        
        yield scrapy.Request(
            url = search_url,
            callback = self.parse_location,
            meta = {
                'item': community
            }
        )
        
        yield self.crawl_deals_of_community(community)
        yield self.crawl_rents_of_community(community)
        
    def parse_location(self, response):
        # self.logger.info('爬取位置')
        text = response.body.decode(response.encoding)
        json = j.loads(text)
        
        if json and json['message'] == 'ok' and len(json['results']) >= 1:
            result = json['results'][0]
            lat = result['location']['lat']
            lng = result['location']['lng']            
            # self.logger.info('爬取 小区位置, %s %s', response.meta['community']['name'], str(result['location']))
            response.meta['item']['location'] = result['location']
            response.meta['poi_list'] = [
                {'query': '交通设施', 'tags': ['地铁站', '公交车站'], 'keys': ['subways', 'buses']},
                {'query': '医疗', 'tags': ['医院', '诊所', '药店'], 'keys': ['hospital', 'hospital', 'drug_store']},
                {'query': '教育培训', 'tags': ['小学', '中学', '高等院校', '幼儿园'], 'keys': ['primary_school', 'middle_school', 'collage', 'kindergarten']},
                {'query': '购物', 'tags': ['购物中心', '百货商场', '超市', '市场'], 'keys': ['megamalls', 'megamalls', 'supermarket', 'market']},
                {'query': '金融', 'tags': ['银行', 'ATM'], 'keys': ['bank', 'atm']},
                {'query': '美食', 'tags': ['中餐厅', '外国餐厅', '小吃快餐店', '蛋糕甜品店', '咖啡厅'], 'keys': ['restaurant', 'restaurant', 'restaurant', 'restaurant', 'coffee_house']},
                {'query': '运动健身', 'tags': ['体育场馆', '健身中心'], 'keys': ['gymnasium', 'gym']},
                {'query': '休闲娱乐', 'tags': ['电影院', '休闲广场'], 'keys': ['movie_theater', 'square']},
                {'query': '旅游景点', 'tags': ['公园', '动物园', '植物园', '游乐园', '风景区'], 'keys': ['park', 'park', 'park', 'park', 'park']},
            ]
            response.meta['page_num'] = 0
            return self.parse_poi(response)
            
        else:
            return response.meta['item']
    
    def parse_poi_in_page(self, response): 
        loc = response.meta['item']['location'] 
        
        if response.meta.get('poi_info') != None:
            poi_info = response.meta['poi_info']
            text = response.body.decode(response.encoding)
            json = j.loads(text)
            
            if json and json['message'] == 'ok' and len(json['results']) > 0:
                results = json['results']
                for i, tag in enumerate(poi_info['tags']):
                    tag_infos = response.meta['item'].get(poi_info['keys'][i])
                    if tag_infos == None:
                        tag_infos = []
                        response.meta['item'][poi_info['keys'][i]] = tag_infos
                    
                    # 根据 tag 的名字筛选
                    tag_infos += [
                        x['name'] for x in filter(
                            lambda x: x['detail_info'].get('tag') 
                            and x['detail_info']['tag'].find(tag) != -1, 
                            results
                        )
                    ]
                
                
                if len(results) == 10:
                    # 有可能下一页
                    page_num = response.meta['page_num'] + 1
                    poi_url = BAIDU_POI.format(poi_info['query'], loc['lat'], loc['lng'], page_num)
                    return scrapy.Request(
                        url = poi_url,
                        callback = self.parse_poi_in_page,
                        meta = {
                            'item': response.meta['item'],
                            'poi_info': poi_info,
                            'poi_list': response.meta['poi_list'],
                            'page_num': page_num
                        }                
                    )
                    
        return self.parse_poi(response)
                
                        
    
    def parse_poi(self, response):
        loc = response.meta['item']['location']           
        
        # 所有的 poi信息都获取完了
        if len(response.meta['poi_list']) == 0:
            response.meta['poi_info'] = None
            return response.meta['item']
            
        # 获取下一个需要的 POI
        else:            
            poi_info = response.meta['poi_list'].pop(0)
            
            # 爬取第 0 页面
            poi_url = BAIDU_POI.format(poi_info['query'], loc['lat'], loc['lng'], 0)
            
            return scrapy.Request(
                url = poi_url,
                callback = self.parse_poi_in_page,
                meta = {
                    'item': response.meta['item'],
                    'poi_info': poi_info,
                    'poi_list': response.meta['poi_list'],
                    'page_num': 0
                }
                
            ) 
    
    def crawl_rents_of_community(self, community):
        url = 'https://{0}.zu.ke.com/zufang/rs{1}/'.format(community['city'], community['name']) 
        
        return scrapy.Request(
            url = url,
            callback = self.parse_rents_of_community,
            meta = {
                'community': community,
            }
        )

    
    def parse_rents_of_community(self, response):


        community = response.meta['community']
        
        total = int(response.xpath('//p[contains(., "为您找到")]/span/text()').get())
        
        if total == 0:
            return None
        
        return self.crawl_rents_in_page(1, community, total)

    
    def craw_rents_in_page(self, page, community, total):
        
        url = 'https://{0}.zu.ke.com/zufang/pg{2}/rs{1}'.format(community['city'], community['name'], page)
        
        return scrapy.Request(
            url = url,
            callback = self.parse_rents_in_page,
            meta = {
                'community': community,
                'page': page,
                'total': total
            }
        )
    
    def parse_rents_in_page(self, response):
        
        total = response.meta['total']
        page = response.meta['page']
        community = response.meta['community']
        
        ul = response.xpath('//div[@class="content__list"]/div[@class="content__list--item"]')
        
        rent = Rent()
        
        for li in ul:
            rent['name'] = li.xpath('.//p[contains(@class, "content__list--item--title")]/a/text()').get().strip()
            rent['community'] = community['name']
            rent['link'] =  'https://{0}.zu.ke.com{1}'.format(response.meta['community']['city'], li.xpath('.//@href').get())
            rent['tags'] = li.xpath('.//p[contains(@class, "content__list--item--bottom")]/i/text()').extract()
            yield scrapy.Request(
                url = rent['link'],
                callback = self.parse_rent,
                meta = {
                    'rent': rent
                }
            )
            
        total -= len(ul)
        
        if total > 0:
            return self.carwl_rents_in_page(page + 1, community, total)
    
    def parse_rent(self, response):
        rent = response.meta['rent']
        
        rent['租赁方式'] = response.xpath('//span[contains(., "租赁方式")]/../text()').get()
        
        def get_val(key):
            return response.xpath('//li[contains(., "{0}")]/text()'.format(key)).get().split('：')[-1]
        
        rent['size'] = get_val('面积').replace('㎡', '')
        rent['maintains'] = get_val('维护')
        rent['level'] = get_val('楼层')
        rent['parking_place'] = get_val('车位')
        rent['electricity'] = get_val('用电')
        rent['heating'] = get_val('采暖')
        rent['lease_term'] = get_val('租期')
        rent['check_house'] = get_val('看房')
        rent['orientation'] = get_val('朝向')
        rent['check_in_time'] = get_val('入住')
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
            
    def crawl_deals_of_community(self, community):
        url = 'https://{0}.ke.com/chengjiao/pg{2}rs{1}/'.format(community['city'], community['name'], 1) 
        
        return scrapy.Request(
            url = url,
            callback = self.parse_deals_in_page,
            meta = {
                'community': community,
            }
        )
    
    def parse_deals_of_community(self, response):
        content = response.xpath('//div[@class="leftContent"]')[0]
        total = int(content.xpath('.//div[contains(@class, "total")]/span/text()').get())
        
        if total != 0:
            page_datas = content.xpath('//@page-data')
            if len(page_datas) != 0:
                total_page = j.loads(page_datas.get())['totalPage']
                for i in range(1, total_page + 1):
                    yield self.crawl_deals_in_page(i, response.meta['community'])
        
    def crawl_deals_in_page(self, page, community):
        url = 'https://{0}.ke.com/chengjiao/pg{2}rs{1}/'.format(community['city'], community['name'], page)
        
        return scrapy.Request(
            url = url,
            callback = self.parse_deals_in_page,
            meta = {
                'community': community
            }
        )
    
    def parse_deals_in_page(self, response):
        content = response.xpath('//div[@class="leftContent"]')[0]
        ul = content.xpath('//ul[@class="listContent"]//li')
        community = response.meta['community']

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
            
    def parse_deal(self, response):
        
        deal = response.meta['deal']
        
        msg = response.xpath('//div[@class="msg"]')
        
        if len(msg) > 0:
            msg = msg[0]
        
            try:
        
                deal['init_price'] = msg.xpath('span[contains(.,"挂牌价格")]/label/text()').get().strip()
                deal['deal_cycle'] = msg.xpath('span[contains(.,"成交周期")]/label/text()').get().strip()
        
                deal['price_adjustment'] = msg.xpath('span[contains(.,"调价")]/label/text()').get().strip()
                deal['check_times'] = msg.xpath('span[contains(.,"带看")]/label/text()').get().strip()
                deal['stars'] = msg.xpath('span[contains(.,"关注")]/label/text()').get().strip()
                deal['glance_over'] = msg.xpath('span[contains(.,"浏览")]/label/text()').get().strip()
            except Exception as e:
                self.logger.warning('info panel not complete %s', e)
            
        
        base = response.xpath('//div[@class="base"]')[0]
        
        deal['layout'] = base.xpath('.//span[contains(.,"房屋户型")]/../text()').get().strip()
        
        deal['building_size'] = base.xpath('.//span[contains(.,"建筑面积")]/../text()').get().strip().replace('㎡', '')
        deal['actual_size'] = base.xpath('.//span[contains(.,"套内面积")]/../text()').get().strip().replace('㎡', '')
        level_str = base.xpath('.//span[contains(.,"所在楼层")]/../text()').get().strip()
        
        deal['level'] = re.findall('(.*)楼层', level_str)
        deal['total_level'] = re.findall('共(.*)层', level_str)
        
        deal['orientation'] = base.xpath('.//span[contains(.,"房屋朝向")]/../text()').get().strip()
        
        try:
            deal['usage'] = float(actual_size) / float(building_size)
        except:
            self.logger.info('房源 %s 的 面积有问题',deal['link'])
            
        deal['layout_structure'] = base.xpath('.//span[contains(.,"户型结构")]/../text()').get().strip()
        
        deal['building_type'] = base.xpath('.//span[contains(.,"建筑类型")]/../text()').get().strip()
        deal['building_structure'] = base.xpath('.//span[contains(.,"建筑结构")]/../text()').get().strip()
        deal['construct_year'] = base.xpath('.//span[contains(.,"建成年代")]/../text()').get().strip()
        deal['echelon_ratio'] = base.xpath('.//span[contains(.,"梯户比例")]/../text()').get().strip()
        
        deal['has_elevator'] = base.xpath('.//span[contains(.,"配备电梯")]/../text()').get().strip()

        deal['decoration'] = base.xpath('.//span[contains(.,"装修情况")]/../text()').get().strip()
        
        deal['heating'] = base.xpath('.//span[contains(.,"供暖方式")]/../text()').get().strip()
        
        transaction = response.xpath('//div[@class="transaction"]')[0]
        
        deal['lianjia_id'] = transaction.xpath('.//span[contains(.,"链家编号")]/../text()').get().strip()
        deal['deal_class'] = transaction.xpath('.//span[contains(.,"交易权属")]/../text()').get().strip()
        deal['init_time'] = transaction.xpath('.//span[contains(.,"挂牌时间")]/../text()').get().strip()
        deal['house_age'] = transaction.xpath('.//span[contains(.,"房屋年限")]/../text()').get().strip()
        deal['house_usage'] = transaction.xpath('.//span[contains(.,"房屋用途")]/../text()').get().strip()
        deal['house_ownership'] = transaction.xpath('.//span[contains(.,"房权所属")]/../text()').get().strip()
        
        deal['tags'] = response.xpath('//div[text()="房源标签"]/../div/a/text()').extract()
        
        return deal
        