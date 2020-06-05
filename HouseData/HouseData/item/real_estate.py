import scrapy

from .basic import BasicItem

    
class RealEstate(BasicItem):
    _id = scrapy.Field()
    
    # 名字
    name = scrapy.Field()
    
    # 城市
    city = scrapy.Field()
    
    # 大区域
    district = scrapy.Field()
    # 小区域
    region = scrapy.Field()
    
    # 物业
    real_estate = scrapy.Field()
    # 物业费用
    real_estate_price = scrapy.Field()
    
    # 标签
    tags = scrapy.Field()
    
    # 参考单价 
    avg_unit_price = scrapy.Field() 

    # 经纬度
    location = scrapy.Field()
    

    # 地铁
    subways = scrapy.Field()
    # 公交
    buses = scrapy.Field()
    # 医院
    hospital = scrapy.Field()
    # 药店
    drug_store = scrapy.Field()
    # 小学
    primary_school = scrapy.Field()
    # 中学
    middle_school = scrapy.Field()
    # 大学
    collage = scrapy.Field()
    # 幼儿园
    kindergarten = scrapy.Field()
    
    # 购物中心 
    megamalls = scrapy.Field()
    # 超市
    supermarket = scrapy.Field()
    # 市场
    market = scrapy.Field()
    
    # 银行
    bank = scrapy.Field()
    # ATM
    atm = scrapy.Field()
    # 餐厅
    restaurant = scrapy.Field()
    # 咖啡馆
    coffee_house = scrapy.Field()
    
    # 公园
    park = scrapy.Field()
    # 电影院
    movie_theater = scrapy.Field()
    # 健身房
    gym = scrapy.Field()
    # 体育馆
    gymnasium = scrapy.Field()
    # 休闲广场
    square = scrapy.Field()
    
    location = scrapy.Field()
    
    # 户型
    
    # {
    #     居室
    #     建面
    #     均价
    #}
    
    layouts = scrapy.Field()
    
    # 最新开盘
    open_date = scrapy.Field()
    
    # 建筑类型
    building_type = scrapy.Field()
    # 占地面积
    floor_area = scrapy.Field()
    # 建筑面积
    floor_space = scrapy.Field()
    # 规划户数
    house_num = scrapy.Field()
    # 产权年限
    property_right_years = scrapy.Field()
    # 最近交房
    latest_transfer = scrapy.Field()
    # 绿化率
    greening_rate = scrapy.Field()
    # 容积率
    floor_area_rate = scrapy.Field()
    # 物业类型
    estate_type = scrapy.Field()
    
    # 车位配比
    parking_place_ratio = scrapy.Field()
    # 采暖方式
    heating = scrapy.Field()
    # 供水
    water = scrapy.Field()
    # 供电
    electricity = scrapy.Field()