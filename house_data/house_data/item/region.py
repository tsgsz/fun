import scrapy


class Region(scrapy.Item):
    # 唯一ID
    _id = scrapy.Field()
    
    # 小区域代号
    code = scrapy.Field()
    
    # 城市 
    city = scrapy.Field()
    # 名字
    name = scrapy.Field()
    # 城市代号
    city_code = scrapy.Field()
    
    # 大区域代号
    district_code = scrapy.Field()
    # 大区域
    district = scrapy.Field()
    