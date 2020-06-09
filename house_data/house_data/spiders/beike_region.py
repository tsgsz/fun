# -*- coding: utf-8 -*-
import scrapy

from ..item.region import Region

DISTRICT_region_XPATH = '//div[3]/div[1]/dl[2]/dd/div/div[2]/a'
CITY_DISTRICT_XPATH = '///div[3]/div[1]/dl[2]/dd/div/div/a'

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



class BeikeRegionSpider(scrapy.Spider):
    name = 'beike_region'
    allowed_domains = ['ke.com']
    start_urls = ['http://ke.com/']
    
    chinese_district_dict = dict()     # 城市代码和中文名映射

    def __init__(self, cities='bj,cd,cq,cs,dg,dl,fs,gz,hz,hf,jn,nj,qd,sh,sz,su,sy,tj,wh,xm,yt', *args, **kwargs):
        super(BeikeSpider, self).__init__()
        self.cities = cities.split(',')
        
        self.start_urls = ['https://{0}.ke.com'.format(self.cities[0])]

    def parse(self, response):
        ret = []
        for city in self.cities:
            ret.append(self.crawl_districts_of_city(city))
        return ret
    
    
    # 爬取区块
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
            
        ret = []

        for i, name in enumerate(en_names):
            self.chinese_district_dict[name] = ch_names[i]
            ret.append(self.crawl_regions_in_district(name, city))
            
        return ret


    # 爬取地区
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
        
        ret = []
        
        for link in context:
            relative_link = link.attrib['href']
            relative_link = relative_link[:-1]
            region = relative_link.split("/")[-1]
            if region != district:
                chinese_region = link.extract()
                self.chinese_region_dict[region] = chinese_region
                
                region = Region()
                region['city_code'] = city
                region['district_code'] = district
                region['code'] = region
                region['_id'] = city + district + region
                region['city'] = CITY_DICT[city]
                region['name'] = chinese_region
                region['district'] = self.chinese_district_dict[district]
                ret.append(region)
        
        return ret