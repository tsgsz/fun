# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo

class MongoDbPipeline:
    
    def __init__(self, db):
        self.db = db

    @classmethod
    def from_settings(cls, settings):
        client = pymongo.MongoClient(settings['MONGO_DB_URL'])
        db = client[settings['DBNAME']]
        return cls(db)
    
    def process_item(self, item, spider):
        cls = item.__class__.__name__
        table = self.db[cls]
        
        table.insert(item)
        return item
    