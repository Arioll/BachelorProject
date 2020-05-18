# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from peewee import Model, MySQLDatabase
from parsers.settings import DATABASE_CONFIG, KEYSUBWORDS_FILTER
from parsers.NER import NER
import peewee
import time
import json
import os

config = DATABASE_CONFIG
db = MySQLDatabase(config['dbname'], user=config['user'], passwd=config['password'], host=config['host'], port=config['port'])
db.connect()

cache_size = 100

class JSONField(peewee.TextField):
    def db_value(self, value):
        return json.dumps(value)

    def python_value(self, value):
        if value is not None:
            return json.loads(value)

class Article(Model):

    global_id = peewee.PrimaryKeyField()

    title = peewee.CharField()
    description = peewee.CharField()
    link = peewee.CharField()
    pub_date = peewee.DateTimeField()

    # Used to identificate new in provider
    provider_name = peewee.CharField()
    local_id = peewee.CharField()

    # Used in search engine
    named_entities = JSONField(null=True)
    appendix = peewee.CharField(null=True)

    class Meta:
        database = db



class ParsersPipeline:

    def __init__(self):
        self.cache = []
        self.i = 0
        self.parsed_links = set()
        for art in Article.select().iterator():
            self.parsed_links.add(art.link)
        self.ner_model = NER()

    def filter_by_subwords(self, item):
        str_arr = (item['title'] + ' ' + item['descr']).lower().split(' ')
        for s in str_arr:
            for sw in KEYSUBWORDS_FILTER:
                if sw in s:
                    return True
        return False

    def save_cache_into_db(self):
        print("SAVE RESULTS INTO THE DATABASE")
        results = [i.get_dictionary() for i in self.cache]

        #strings = [i['title'] + ' ' + i['descr'] for i in self.cache]
        #ner_decomp = self.ner_model.ner_decomposition(strings)
        #for res, ner in zip(results, ner_decomp):
        #    res['named_entities'] = ner[0]
        #    res['appendix'] = ner[1]

        with db.atomic():
            Article.insert_many(results).execute(db)
        self.cache = []
        self.i = 0

    def process_item(self, item, spider):
        if self.i < cache_size:
            if self.filter_by_subwords(item) and item['link'] not in self.parsed_links:
                self.cache.append(item)
                self.parsed_links.add(item['link'])
                self.i += 1
        else:
            self.save_cache_into_db()
        return item

    def close_spider(self, spider):
        self.save_cache_into_db()
