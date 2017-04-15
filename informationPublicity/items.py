# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class InformationpublicityItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    status = scrapy.Field()
    code = scrapy.Field()
    user = scrapy.Field()
    date = scrapy.Field()
    historyName = scrapy.Field()
    pass
