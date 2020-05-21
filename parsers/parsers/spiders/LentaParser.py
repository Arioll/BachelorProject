import time
import scrapy
import re

from ..items import ParsersItem


class LentaParser(scrapy.Spider):

    name = 'lenta'

    def __init__(self):
        self.home_page = 'https://lenta.ru/2020/05/20/'
        self.main_page = 'https://lenta.ru'

        self.more_index = 1
        self.article_selector = 'div.item a::attr(href)'
        self.title_selector = 'h1::text'
        self.descr_selector = 'h2::text'
        self.pub_date_selector = 'div.b-topic__info time::attr(datetime)'

    def start_requests(self):
        yield scrapy.Request(self.home_page, callback=self.parse)

    def parse(self, response):

        urls = response.css(self.article_selector).getall()
        for url in urls:
            if url.split('/')[1] not in ['articles', 'news']:
                continue
            print("Downloading url: " + url)
            yield scrapy.Request(self.main_page + url, callback=self.parse_page)

        next_page = response.css('a.control_mini::attr(href)').get()
        if next_page is not None:
            next_page = self.main_page + next_page
            yield scrapy.Request(next_page, callback=self.parse)

    def extract_text(self, html):
        return re.sub(r'<[^>]*>', '', html) 
            
    def parse_page(self, response):
        item = ParsersItem()

        item['title'] = response.css(self.title_selector).get()
        if item['title'] is None:
            item['title'] = response.css('div.premial-header__title::text').get(default='') \
            + ' ' + response.css('div.premial-header__subtitle::text').get(default='')
            item['title'] = self.extract_text(item['title'].strip())

        item['descr'] = response.css(self.descr_selector).get()
        if item['descr'] is None and response.url.split('/')[1] == 'articles':
            item['descr'] = response.css('span.premial-body__first-letter::text').get(default='') \
            + response.css('p.b-topic__announce::text').get(default='')
            item['descr'] = self.extract_text(item['descr'].strip())
        elif item['descr'] == 'Материалы по теме' or item['descr'] is None:
            item['descr'] = self.extract_text(response.css('p').get())

        item['pub_date'] = response.css(self.pub_date_selector).get()
        item['link'] = response.url
        item['provider_name'] = 'Lenta'

        yield item