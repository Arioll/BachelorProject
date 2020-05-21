import time
import scrapy

from ..items import ParsersItem


class CNewsParser(scrapy.Spider):

    name = 'cnews'

    def __init__(self):
        self.home_page = 'https://cnews.ru/news/60'
        self.main_page = 'https://cnews.ru'

        self.article_selector = 'div.allnews_item a::attr(href)'
        self.next_page_selector = 'a.read_more_btn::attr(href)'
        self.title_selector = 'h1::text'
        self.descr_selector = 'article.news_container p::text'
        self.pub_date_selector = 'div.article_date time::text'

    def start_requests(self):
        yield scrapy.Request(self.home_page, callback=self.parse)

    def parse(self, response):

        urls = response.css(self.article_selector).getall()
        for url in urls:
            print("Downloading url: " + url)
            yield scrapy.Request(url, callback=self.parse_page)

        next_page = response.css(self.next_page_selector).get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            print(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

    def preprocess_datetime(self, dt_string):
        date = dt_string.split(', ')[0]
        time = dt_string.split(', ')[2]
        time += ':00'
        date = '-'.join(reversed(date.split('.')))
        return date + ' ' + time
            
    def parse_page(self, response):
        item = ParsersItem()

        item['title'] = response.css(self.title_selector).get()
        item['descr'] = response.css(self.descr_selector).get()
        item['pub_date'] = self.preprocess_datetime(response.css(self.pub_date_selector).get())
        item['link'] = response.url
        item['provider_name'] = 'CNews'

        yield item