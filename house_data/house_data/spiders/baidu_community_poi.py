# -*- coding: utf-8 -*-
import scrapy

import pymongo
from ..item.deal import Deal
from ..utils import *
import json as j

BAIDU_SEARCH = 'http://api.map.baidu.com/place/v2/search?query={0}&tag=住宅&region={1}&output=json&ak=MQMeFXHTVvCx0hffjXCTj7mrqKhMnpTH&city_limit=true&page_size=1'

BAIDU_POI = 'http://api.map.baidu.com/place/v2/search?query="{0}"&location={1},{2}&radius=2000&output=json&ak=MQMeFXHTVvCx0hffjXCTj7mrqKhMnpTH&scope=2&page_size=20&radius_limit=true&page_num={3}'


class BaiduCommunityPoiSpider(scrapy.Spider):
    name = 'baidu_community_poi'
    allowed_domains = ['baidu.com']
    
    def __init__(self, cities='bj', *args, **kwargs):
        super(BaiduCommunityPoiSpider, self).__init__()
        self.cities = cities.split(',')

    def start_requests(self):
        client = pymongo.MongoClient(self.settings['MONGO_DB_URL'])
        db = client['house_data']
        community_db = db['Community']
        communities = community_db.find(
            {'$or': [{'city': city_code_to_city(city)} for city in self.cities]}
        )
        for c in communities:
            self.logger.info('请求{0}{1}的周边信息'.format(c['city'], c['name']))
            yield scrapy.Request(
                url = BAIDU_SEARCH.format(c['name'], c['city']),
                callback = self.parse_location,
                meta = {
                    'item': c
                }
            )
            
    def parse_location(self, response):
        text = response.body.decode(response.encoding)
        json = j.loads(text)
        
        if json and json['message'] == 'ok' and len(json['results']) >= 1:
            result = json['results'][0]
            lat = result['location']['lat']
            lng = result['location']['lng']            
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
                
                
                if len(results) == 20:
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
