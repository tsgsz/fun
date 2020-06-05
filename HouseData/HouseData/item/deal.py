import scrapy

from .basic import BasicItem

class Deal(BasicItem):
    _id = scrapy.Field()
    # 签约时间
    time = scrapy.Field()
    # 签约单价
    price = scrapy.Field()
    # 签约总价
    total_price = scrapy.Field()
    # 挂单总价
    init_price = scrapy.Field() 
    # 成交周期
    deal_cycle = scrapy.Field()
    # 挂牌时间
    init_time = scrapy.Field()
    
    # 调价
    price_adjustment = scrapy.Field()
    # 带看
    check_times = scrapy.Field()
    # 关注
    stars = scrapy.Field()
    # 浏览次数
    glance_over = scrapy.Field()
    
    # 上次交易时间
    last_trade_time = scrapy.Field()
    # 房屋年限
    house_age = scrapy.Field()
    # 交易权属
    deal_class = scrapy.Field()
    # 房屋用途
    house_usage = scrapy.Field()
    # 房屋所属: 是否共有
    house_ownership = scrapy.Field()
    # 链家编号
    lianjia_id = scrapy.Field()
    
    
    # 小区
    community = scrapy.Field()
    # 楼层
    level = scrapy.Field()
    # 总楼层
    total_level = scrapy.Field()
    # 建成年代
    construct_year = scrapy.Field()
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
    building_structure = scrapy.Field()
    # 梯户比例
    echelon_ratio = scrapy.Field()
    # 是否有电梯
    has_elevator = scrapy.Field()
    # 装修情况
    decoration = scrapy.Field()
    # 供暖情况
    heating = scrapy.Field()