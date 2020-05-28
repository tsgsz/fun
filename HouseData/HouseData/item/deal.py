import scrapy

from .basic import BasicItem

    
class Deal(BasicItem):
    # 房子
    house = scrapy.Field()
    # 房产类型
    house_class = scrapy.Field()
    # 签约时间(挂单)
    time = scrapy.Field()
    # 签约单价(挂单)
    price = scrapy.Field()
    # 签约总价(挂单)
    total_price = scrapy.Field()
    # 是否关闭
    on = scrapy.Field()
    # 是否是租单
    is_rent = scrapy.Field()
    # 上次交易时间
    last_trade_time = scrapy.Field()
    # 房屋年限
    house_age = scrapy.Field()
    # 交易权属
    deal_class = scrapy.Field()
    # 房屋用途
    house_usage = scrapy.Field()
    # 产权所属: 是否共有
    is_owned_by_all = scrapy.Field()
    # 抵押情况
    pledge = scrapy.Field()
    # 房本备件
    premises_permit_backup = scrapy.Field()