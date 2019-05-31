#!/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2019, All Rights Reserved.
# Author: Pine <cdtsgsz@gmail.com>

import docx

class DocReader:
    def __init__(self):
        self.doc = None

    def load(self, file_name = 'data/1.docx'):
        self.doc = docx.Document(file_name)

    def process(self):
        for p in self.doc.paragraphs:
            yield p.text