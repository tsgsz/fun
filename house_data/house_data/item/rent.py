import scrapy

from .basic import BasicItem

class Rent(BasicItem):
    # 名字
    name = scrapy.Field()
    # 面积
    size = scrapy.Field()
    # 维护
    maintains = scrapy.Field()
    # 楼层
    level = scrapy.Field()
    # 朝向
    orientation = scrapy.Field()
    # 车位
    parking_place = scrapy.Field()
    # 入住
    check_in_date = scrapy.Field()
    # 电梯
    elevator = scrapy.Field()
    # 用水
    water = scrapy.Field()
    # 采暖
    heating = scrapy.Field()
    # 燃气
    gas = scrapy.Field()
    # 租期
    lease_term = scrapy.Field()
    # 看房
    check_house = scrapy.Field()
    # 配套
    # compelete_facility = scrapy.Field()
    # 社区
    community = scrapy.Field()
    # 供电
    electricity = scrapy.Field()
    

    
    # 费用
    # total_price = scrapy.Field()
    # 押金
    # margin = scrapy.Field()
    # 付款方式
    # payment_type = scrapy.Field()
    # 服务费
    # tips = scrapy.Field()
    # 中介费
    # commission = scrapy.Field()
    
    # 费用
    pay = scrapy.Field()
    
    # 标签
    tags = scrapy.Field()
    # 租赁方式
    rent_type = scrapy.Field()
    