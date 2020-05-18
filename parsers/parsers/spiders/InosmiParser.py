import time
import scrapy

from ..items import ParsersItem

new_title_tag = "h1"
new_title_class = "js-slide-title"
new_descr_tag = "div"
new_descr_class = "article__text__overview"


class InosmiParser(scrapy.Spider):

    name = 'inosmi'

    def __init__(self):
        self.home_page = 'https://inosmi.ru'
        self.main_page = 'https://inosmi.ru/economic'
        self.search_item_tag = "a"
        self.search_item_class = "rubric-list__article-image rubric-list__article-image_small"

    def start_requests(self):
        yield scrapy.Request(self.main_page, callback=self.parse)

    def parse(self, response):

        urls = response.css('h1 a').re(r'"/economic/.+"')
        for url in urls:
            print("Downloading url: " + url)
            yield scrapy.Request(self.home_page + url.replace('"', ''), callback=self.parse_page)

        next_page = response.css('a.input-button::attr(href)').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)
            
    def parse_page(self, response):
        item = ParsersItem()

        item['title'] = response.css('h1.article-header__title::text').get()
        d1 = response.css('div.article-header__introduction::text').get()
        d2 = response.css('p.article-header__announce::text').get()
        if d1 is None and d2 is None:
            item['descr'] = ''
        elif d1 is None:
            item['descr'] = d2
        elif d2 is None:
            item['descr'] = d1
        else:
            item['descr'] = d2
        item['pub_date'] = response.css('time::attr(datetime)').get()
        item['link'] = response.url
        item['local_id'] = int(response.url.split('/')[-1].split('.')[0])
        item['provider_name'] = 'Inosmi'

        yield item
        

