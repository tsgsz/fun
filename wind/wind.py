#!/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2019, All Rights Reserved.
# Author: Pine <cdtsgsz@gmail.com>

import sys
import docx

class Wind:

    def __init__(self):
        self.name_getter = None
        self.location_getter = None
        self.item_getter = None
        self.relation_getter = None

    def process(self, file_name = 'data/1.docx'):
