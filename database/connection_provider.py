import peewee
import pandas as pd
import string
import json
import os
import re

from peewee import Model, MySQLDatabase
#from common.article import ArticleModel


config_filename = 'db_connection_config.json'
dir_path = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(dir_path, config_filename)

def get_connection_config():
    with open(config_path) as file:
        config = json.load(file)
    return config

config = get_connection_config()
db = MySQLDatabase(config['dbname'], user=config['user'], passwd=config['password'], host=config['host'], port=config['port'])
db.connect()

class JSONField(peewee.TextField):
    def db_value(self, value):
        return str(value)

    def python_value(self, value):
        if value is not None:
            return eval(value)

class Article(Model):

    global_id = peewee.PrimaryKeyField()

    title = peewee.TextField()
    description = peewee.TextField()
    link = peewee.TextField()
    pub_date = peewee.DateTimeField()

    # Used to identificate new in provider
    provider_name = peewee.TextField()
    #local_id = peewee.TextField()

    # Used in search engine
    named_entities = JSONField(null=True)
    appendix = peewee.CharField(null=True)

    class Meta:
        database = db

class ConnectionProvider:

    def drop_table(self):
        Article.drop_table()

    def truncate_table(self):
        Article.truncate_table()

    def check_table(self):
        return Article.table_exists()

    def add_articles(self, articles):

        if not Article.table_exists():
            Article.create_table()

        with db.atomic():
            Article.insert_many([i.get_dictionary() for i in articles]).execute()

    def create_table(self):
        Article.create_table()

    def get_article(self, id):
        return Article.get_by_id(id)
    
    def get_all_articles(self):
        return Article.select()

    def get_range_ids(self, lower, upper):
        return Article.select().where(Article.global_id >= lower & Article.global_id < upper)

    def get_news_by_predicate(self, pred_func):
        return Article.select().where(pred_func(Article))

    def update_articles(self, articles, fields):
        Article.bulk_update(articles, fields)

    def get_articles_by_id_and_provider_name(self, local_id, provider_name):
        return Article.select().where(Article.provider_name == provider_name & Article.local_id == local_id)

    def _preprocess_str(self, s):
        s = re.sub(f'[{string.whitespace}]', ' ', s.strip()) 
        return re.sub(' +', ' ', s)

    def build_csv(self, path, sep=';'):
        fields_names = ['global_id', 'title', 'description', 'link', 
                        'pub_date', 'provider_name', 
                        'named_entities', 'appendix']
        lines = [sep.join(fields_names)]
        for art in Article.select().iterator():
            art_arr = [art.global_id, art.title, art.description, art.link, 
                       art.pub_date, art.provider_name, 
                       art.named_entities, art.appendix]
            lines.append(self._preprocess_str(sep.join([str(i) for i in art_arr])))
        with open(path, 'w') as file:
            file.write('\n'.join(lines))

    def load_csv_into_db(self, path, sep=';'):

        Article.drop_table()
        Article.create_table()

        frame = pd.read_csv(path, sep)
        for i, row in frame.iterrows():
            d = dict(row)
            d['global_id'] = int(d['global_id'])
            new_ent = set()
            for ent in eval(d['named_entities']):
                if ent not in string.punctuation:
                    new_ent.add(ent)
            #print(d['named_entities'])
            d['named_entities'] = list(new_ent)
            Article.insert(d).execute()