import scrapy

from .basic import BasicItem

    
class RealEstate(BasicItem):
    # 户型
    layout = scrapy.Field()
    # 小区
    community = scrapy.Field()
    # 面积
    area = scrapy.Field()
    # 朝向
    direction = scrapy.Field()
    # 建造时间
    construct_time = scrapy.Field()
    # 挂单时间
    time = scrapy.Field()
    # 挂单单价
    price = scrapy.Field()
    # 挂单总价
    total_price = scrapy.Field()
    # 项目标签
    project_tags = scrapy.Field()