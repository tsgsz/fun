#!/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2019, All Rights Reserved.
# Author: Pine <cdtsgsz@gmail.com>

import os
import sys

from doc_reader import DocReader

from thulac_getter import ThuNameGetter
from thulac_getter import ThuLocationGetter
from thulac_getter import ThuItemGetter

class Wind:

    def __init__(self):
        self.name_getter = ThuItemGetter()
        self.location_getter = ThuLocationGetter()
        self.item_getter = ThuItemGetter()
        self.relation_getter = None
        self.doc_reader = DocReader()

    def process(self, dir_name = 'data'):
        if os.path.exists(dir_name) and os.path.isdir(dir_name):
            for file_name in os.listdir(dir_name):
                relative_file_name = dir_name + '/' + file_name
                self.doc_reader.load(relative_file_name)
                names = set()
                locations = set()
                items = set()
                relations = set()
                params = []
                for param in self.doc_reader.process():
                    params.append(param)
                    names = names.union(self.name_getter.process(param))
                    locations = locations.union(self.location_getter.process(param))
                    items = items.union(self.item_getter.process(param))
                    # relations = relations.union(self.relation_getter.process(params, names))

                yield (file_name, names, locations, items, relations)


if __name__ == '__main__':
    path = 'data'
    if (len(sys.argv) > 1):
        path = sys.argv[1]

    wind = Wind()
    for (file_name, names, locations, items, releations) in wind.process(path):
        print("=== 处理文档 <" + file_name + ">===")
        print("找到名字:")
        print(names)
        print("找到地名:")
        print(locations)
        print("找到物品")
        print(items)
        print("找到关系")
        print(releations)
        print("=== 文档处理完毕 ===")