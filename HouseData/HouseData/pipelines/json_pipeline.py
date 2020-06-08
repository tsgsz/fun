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
        self.file = open('employeelist.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    
    def process_item(self, item, spider):
        cls = item.__class__.__name__
        table = self.db[cls]
        
        table.insert(item)
        return item
    