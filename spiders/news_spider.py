import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import re
from urllib.parse import urljoin
from scrapy.loader.processors import MapCompose, TakeFirst
from w3lib.html import remove_tags
import json

def remove_whitespace(value):
    return value.strip()

def serialize(obj):
    if isinstance(obj):
        serial = obj.isoformat()
        return serial

    return obj.__dict__

class NewsItem(scrapy.Item):
    linenum = scrapy.Field()
    link = scrapy.Field()
    title = scrapy.Field()
        input_processor= MapCompose(remove_tags, remove_whitespace),
        output_processor= TakeFirst()
    )
    time = scrapy.Field()
    text = scrapy.Field()
        input_processor= MapCompose(remove_tags, remove_whitespace),
        output_processor= TakeFirst()
    )
    detail = scrapy.Field()
        input_processor= MapCompose(remove_tags, remove_whitespace),
        output_processor= TakeFirst()
    )

class NewsDetail(scrapy.Item):
    detail = scrapy.Field()

class NewsSpider(scrapy.Spider):
    name = "worldcement"
    allowed_domains = ["worldcement.com"]
    start_urls = ["https://www.worldcement.com/news/"]

    rules = [
        Rule(LinkExtractor(restrict_xpaths="//td[not(@*)]/div[not(@*)]/a[not(@class)]"),
             callback="parse_items",
             follow=True),
    ]
    def parse(self,response):
        self.log('I just visited: ' + response.url)
        row = 0
        for data in response.css('div#maincontent'):
            for next_page in data.css('h2.article-title > a'):
                row = row + 1
                item = NewsItem()
                item['linenum'] = row
                item['title'] = data.css('h2.article-title > a::text').extract()
                item['time'] = data.css('small > time::attr(datetime)').extract()
                item["text"] = data.css("p::text").extract()
                item['link'] = next_page
                #yield response.follow(next_page, self.parse_article,meta={'item': item})
                request = response.follow(next_page, self.parse_article)
                request.meta["linenum"] = item['linenum']
                request.meta["title"] = item['title']
                request.meta["time"] = item['time']
                request.meta["text"] = item['text']
                yield request
    def parse_article(self, response):
        for data2 in response.css('div#maincontent'):
            #detail = NewsDetail()
            detail = data2.css('article[class="article article-detail"] div[itemprop="articleBody"] p::text').extract()
            linenum = response.meta['linenum']
            title = response.meta['title']
            time = response.meta['linenum']
            text = response.meta['text'] 
        yield {'linenum': linenum,
               'title':title,
               'time': time,
               'text': text,
               'detail': detail,
              }
        #yield {'items': ''.join(detail['detail'])}