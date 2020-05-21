# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ParsersItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    descr = scrapy.Field()
    #local_id = scrapy.Field()
    provider_name = scrapy.Field()
    link = scrapy.Field()
    pub_date = scrapy.Field()

    def get_dictionary(self):
        return {'title': self['title'],
                'description': self['descr'],
                'link': self['link'],
                'pub_date': self['pub_date'],
                'provider_name': self['provider_name']}
                #'local_id': self['local_id']}
