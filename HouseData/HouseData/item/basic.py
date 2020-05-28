import scrapy


class BasicItem(scrapy.Item):
    # 链接
    link = scrapy.Field()
