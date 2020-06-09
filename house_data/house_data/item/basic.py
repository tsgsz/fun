import scrapy


class BasicItem(scrapy.Item):
    # 链接
    link = scrapy.Field()
    # 数据ID
    _id = scrapy.Field()
