CREATE DATABESE /*!32312 IF NOT EXISTS*/ `HouseData` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `HouseData`;

DROP TABLE IF EXISTS `Community`;

CREATE TABLE `Community` (
    `community_id` VARCHAR(20) NOT NULL, 
    `name` VARCHAR(30) NOT NULL,
    `city` VARCHAR(10) NOT NULL,
    
    `district` VARCHAR(10) NOT NULL,
    `region` VARCHAR(10) NOT NULL,
    
    `real_estate` VARCHAR(30),
    
    `real_estate_price` INT,
    
    `tags` VARCHAR(500),
    
    `avg_unit_price` INT,

    `location` VARCHAR(200)
    
    `subways` = scrapy.Field()
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
)
