import scrapy

from .basic import BasicItem

    
class SecondHandHouse(BasicItem):
    # 小区
    community = scrapy.Field()
    # 楼层
    level = scrapy.Field()
    # 建造时间
    construct_time = scrapy.Field()
    # 标签
    tags = scrapy.Field()
    # 朝向
    orientation = scrapy.Field()
    # 使用率
    usage = scrapy.Field()
    # 套内面积
    actual_size = scrapy.Field()
    # 建筑面积
    building_size = scrapy.Field()
    # 户型
    layout = scrapy.Field()
    # 户型结构
    layout_structure = scrapy.Field()
    # 建筑类型
    building_type = scrapy.Field()
    # 建筑结构
    building_construct = scrapy.Field()
    # 是否有电梯
    has_elevator = scrapy.Field()
    # 装修情况
    decoration = scrapy.Field()
    # 供暖情况
    heating = scrapy.Field()
    