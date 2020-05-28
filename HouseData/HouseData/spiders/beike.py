# -*- coding: utf-8 -*-
import scrapy
import json

from .basic import BasicSpider

from ..item.community import Community


DISTRICT_region_XPATH = '//div[3]/div[1]/dl[2]/dd/div/div[2]/a'
CITY_DISTRICT_XPATH = '///div[3]/div[1]/dl[2]/dd/div/div/a'

BAIDU_SEARCH = 'http://api.map.baidu.com/place/v2/search?query={0}&ttag=住宅&region={1}&output=json&ak=MQMeFXHTVvCx0hffjXCTj7mrqKhMnpTH&city_limit=true&page_size=1'
BAIDU_POI = 'http://api.map.baidu.com/place/v2/search?query="{0}"&location={1},{2}&radius=2000&output=json&ak=MQMeFXHTVvCx0hffjXCTj7mrqKhMnpTH&scope=2&page_size=10&radius_limit=true&page={3}'

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

class BeikeSpider(BasicSpider):
    name = 'beike'
    allowed_domains = ['ke.com']

    chinese_district_dict = dict()     # 城市代码和中文名映射
    chinese_region_dict = dict()       # 版块代码和中文名映射
    chinese_region_dict = dict()


    def __init__(self, cities, *args, **kwargs):
        super(BeikeSpider, self).__init__()
        self.cities = cities.split(',')
        print(self.cities)
        self.start_urls = ['https://{0}.ke.com'.format(self.cities[0])]

    def parse(self, response):
        #暂时不需要登录

        for city in self.cities:
            yield self.crawl_districts_of_city(city)

    def crawl_districts_of_city(self, city):
        district_url = 'https://{0}.ke.com/xiaoqu'.format(city)
        return scrapy.Request(
                url = district_url,
                headers = self.header(),
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
            ch_names.append(ele.xpath('//text()')[0])

        for i, name in enumerate(en_names):
            self.chinese_district_dict[name] = ch_names[i]

            yield self.crawl_regions_in_district(name, city)



    def crawl_regions_in_district(self, district, city):
        region_url = 'https://{0}.ke.com/xiaoqu/{1}'.format(city, district)
        return scrapy.Request(
            url = region_url,
            headers = self.header(),
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

    def crawl_communities_in_region(self, region, district, city):
        self.logger.info('爬取 region: %s', region)
        communities_url = 'https://{0}.ke.com/xiaoqu/{1}/'.format(city, region)
        return scrapy.Request(
            url = communities_url,
            headers = self.header(),
            callback = self.parse_communities,
            meta = {
                'city': city,
                'district': district,
                'region': region
            }
        )

    def parse_communities(self, response):
        content = response.xpath('//div[@class="content"]')[0]

        total = int(content.xpath('//h2[contains(@class, "total")]/span/text()')[0].get())

        
        if total == 0:
            return []

        # yield self.parse_communities_in_page(response)

        district = response.meta['district']
        city = response.meta['city']
        region = response.meta['region']

        page_datas = content.xpath('//@page-data')
        if len(page_datas) != 0:
            total_page = json.loads(page_datas[0].get())['totalPage']
            for i in range(1, total_page + 1):
                yield self.crawl_communities_in_page(i, region, district, city)

    def crawl_communities_in_page(self, page, region, district, city):
        self.logger.info('爬取 region, page: %s %s', region, page)
        community_url = 'https://{0}.ke.com/xiaoqu/{1}/pg{2}'.format(city, region, page)
        return scrapy.Request(
            url = community_url,
            headers = self.header(),
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

        ul = content.xpath('//ul[@class="listContent"]//li')


        for li in ul:
            tags = li.xpath('//div[@class="tagList"]/span//text()').get()
            detail_url = li.xpath('a/@href')[0].get()
            community_id = li.xpath('//@data-housecode')[0].get()

            community = Community()
            community['community_id'] = community_id
            community['tags'] = tags
            community['city'] = city
            community['district'] = district
            community['region'] = region
            community['link'] = detail_url
            yield scrapy.Request(
                url = detail_url,
                headers = self.header(),
                callback = self.parse_community,
                meta = {
                    'community': community
                }
            )

    def has_value(self, list_value):
        return list_value and len(list_value) >= 1
        
    def parse_community(self, response):

        detail_page = response.xpath('//div[@class="xiaoquDetailPage"]')[0]
        title = detail_page.xpath('//div[@data-component="detailHeader"]//div[@class ="title"]/h1/text()')[0].get().strip()


        community_desc = detail_page.xpath('//div[contains(@class, "xiaoquDescribe")]')[0]

        node = community_desc.xpath('//span[text() = "物业费用"]//following::span[1]//text()')
        if self.has_value(node):
            real_estate_price = node[0].get().strip()
            response.meta['community']['real_estate_price'] = real_estate_price
            
        node = community_desc.xpath('//span[text() = "物业公司"]//following::span[1]//text()')
        if self.has_value(node):
            real_estate = node[0].get().strip()
            response.meta['community']['real_estate'] = real_estate
            
        node = community_desc.xpath('//span[@class="xiaoquUnitPrice"]//text()')
        if self.has_value(node):
            avg_unit_price = node[0].get().strip()
            response.meta['community']['avg_unit_price'] = avg_unit_price
        
        response.meta['community']['name'] = title
        
        self.logger.info('爬取 小区信息, %s', title)

        
        # 获取 POI 数据
        # 获取经纬度
        cn_city = CITY_DICT[response.meta['community']['city']]
        search_url = BAIDU_SEARCH.format(title, cn_city) 
        
        return scrapy.Request(
            url = search_url,
            headers = self.header(),
            callback = self.parse_location,
            meta = response.meta
        )
        
    def parse_location(self, response):

        json = response.json()
        
        if json and json['message'] == 'ok' and len(json['results']) >= 1:
            result = json['results'][0]
            lat = result['location']['lat']
            lng = result['location']['lng']            
            self.logger.info('爬取 小区位置, %s %s', response.meta['community']['name'], str(result['location']))
            response.meta['community']['location'] = result['location']
            response.meta['poi_list'] = [
                {'query': '交通设施', 'tags': ['地铁站', '公交站'], 'keys': ['subways', 'buses']},
                {'query': '医疗', 'tags': ['医院', '诊所', '药店'], 'keys': ['hospital', 'hospital', 'drug_store']},
                {'query': '教育培训', 'tags': ['小学', '中学', '高等院校', '幼儿园'], 'keys': ['primary_school', 'middle_school', 'collage', 'kindergarten']},
                {'query': '购物', 'tags': ['购物中心', '百货商场', '超市', '市场'], 'keys': ['megamalls', 'megamalls', 'supermarket', 'market']},
                {'query': '金融', 'tags': ['银行', 'ATM'], 'keys': ['bank', 'atm']},
                {'query': '美食', 'tags': ['中餐厅', '外国餐厅', '小吃快餐店', '蛋糕甜品店', '咖啡厅'], 'keys': ['restaurant', 'restaurant', 'restaurant', 'coffee_house']},
                {'query': '运动健身', 'tags': ['体育场馆', '健身中心'], 'keys': ['gymnasium', 'gym']},
                {'query': '休闲娱乐', 'tags': ['电影院', '休闲广场'], 'keys': ['movie_theater', 'square']},
                {'query': '旅游景点', 'tags': ['公园', '动物园', '植物园', '游乐园'], 'keys': ['park', 'park', 'park', 'park']},
            ]
            response.meta['page_num'] = 0
            return self.parse_poi(response)
            
        else:
            return response.meta['community']
            
    def parse_poi(self, response):
        loc = response.meta['location']
        
        # 获取 POI 信息
        if response.meta.get('poi_info') != None:
            poi_info = response.meta['poi_info']
            json = response.json()
            self.logger.info('爬取 小区poi, %s %s', response.meta['community']['name'], str(poi_info))

            
            if json and json['message'] == 'ok' and len(json['results']) > 0:
                results = json['results']
                for i, tag in enumerate(poi_info['tags']):
                    tag_infos = response.meta['community'].get(poi_info['keys'][i])
                    if tag_infos == None:
                        tag_infos = []
                        response.meta['community'][poi_info['keys'][i]] = tag_infos
                    
                    # 根据 tag 的名字筛选
                    tag_infos += [x['name'] for x in filter(lambda x: x['detail_info'].get('tag') and x['detail_info']['tag'].find(tag) != -1, json['results'])]
                    
                # 下一页
                page_num = response.meta['page_num'] + 1
                poi_url = BAIDU_POI.format(poi_info['query'], loc['lat'], lat['lng'], page_num)
                yield scrapy.Request(
                    url = poi_url,
                    headers = self.header(),
                    callback = self.parse_poi,
                    meta = {
                        'community': response.meta['community'],
                        'location': {'lat': lat, 'lng': lng},
                        'poi_info': poi_info,
                        'poi_list': response.meta['poi_list'],
                        'page_num': page_num
                    }                
                )
                
                    
        
        # 所有的 poi信息都获取完了
        if len(response.meta['poi_list']) == 0:
            
            if response.meta['callback']:
                yield response.meta['callback'](response)
            
            else:
                yield response.meta['community']
            
        # 获取下一个需要的 POI
        else:            
            poi_info = response.meta['poi_list'].pop(0)
            
            
            # 爬取第 0 页面
            poi_url = BAIDU_POI.format(poi_info['query'], loc['lat'], lat['lng'], 0)
            
            yield scrapy.Request(
                url = poi_url,
                headers = self.header(),
                callback = self.parse_poi,
                meta = {
                    'community': response.meta['community'],
                    'location': {'lat': lat, 'lng': lng},
                    'poi_info': poi_info,
                    'poi_list': response.meta['poi_list'],
                    'page_num': 0
                }
                
            )            
            
            
        
        
        
        
            
            
        
        
        
        
        