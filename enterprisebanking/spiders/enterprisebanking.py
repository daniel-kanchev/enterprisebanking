import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from enterprisebanking.items import Article


class enterprisebankingSpider(scrapy.Spider):
    name = 'enterprisebanking'
    start_urls = ['https://www.enterprisebanking.com/']

    def parse(self, response):
        links = response.xpath('//main[@class="articles"]//a[@class="learnmore"]/@href').getall()
        yield from response.follow_all(links, self.find_new)

    def find_new(self, response):
        yield response.follow(response.url, self.parse_article, dont_filter=True)

        links = response.xpath('//a[@class="learnmore"]/@href').getall()
        yield from response.follow_all(links, self.find_new)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//time/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="content"]/main//text()').getall()
        content = [text for text in content if text.strip() and '{' not in text]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
