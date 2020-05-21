import time
import scrapy

from ..items import ParsersItem


class KomersantParser(scrapy.Spider):

    name = 'komersant'

    def __init__(self):
        self.home_page = 'https://www.kommersant.ru'
        self.main_page = 'https://www.kommersant.ru/archive/news?from=news'

        self.article_selector = 'li.archive_date_result__item a::attr(href)'
        self.next_page_selector = 'div.archive_date__field a::attr(href)'
        self.title_selector = 'h1.article_name::text'
        self.descr_selector = 'div.article_text_wrapper p::text'
        self.pub_date_selector = 'time::attr(datetime)'

    def start_requests(self):
        yield scrapy.Request(self.main_page, callback=self.parse)

    def parse(self, response):

        urls = response.css(self.article_selector).getall()
        for url in urls:
            print("Downloading url: " + url)
            yield scrapy.Request(self.home_page + url, callback=self.parse_page)

        next_page = response.css(self.next_page_selector).get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            print(next_page)
            yield scrapy.Request(next_page, callback=self.parse)
            
    def parse_page(self, response):
        item = ParsersItem()

        item['title'] = response.css(self.title_selector).get()
        item['descr'] = response.css(self.descr_selector).get()
        item['pub_date'] = response.css(self.pub_date_selector).get()
        item['link'] = response.url
        item['provider_name'] = 'Komersant'

        yield item
        
    