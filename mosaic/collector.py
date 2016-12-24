import urllib.parse

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.loader import ItemLoader

BASE_URL = 'https://www.google.se'


class ImageItem(scrapy.Item):
    images = scrapy.Field()
    image_urls = scrapy.Field()


class ImageSpider(scrapy.Spider):
    name = 'imagecrawler'

    def __init__(self, *args, **kwargs):
        self.page_count = kwargs.pop('page_count')
        super().__init__(*args, **kwargs)

    def parse(self, response):
        loader = ItemLoader(item=ImageItem(), response=response)
        loader.add_xpath(
            'image_urls',
            '//table[@class="images_table"]//img/@src'
        )
        yield loader.load_item()

        next_link = response.xpath('//table[@id="nav"]//a/@href').extract()[-1]
        if next_link and self.page_count:
            yield scrapy.Request(BASE_URL + next_link)
            self.page_count -= 1


def collect(keywords, data_dir, page_count):
    process = CrawlerProcess({
        'USER_AGENT': 'mosaic-collector/0.1',
        'ITEM_PIPELINES': {'scrapy.pipelines.images.ImagesPipeline': 1},
        'IMAGES_STORE': data_dir,
        'COOKIES_ENABLED': False
    })

    start_url = BASE_URL + '/search?' + urllib.parse.urlencode(
        {'q': ' '.join(keywords),
         'tbm': 'isch'}
    )
    process.crawl(ImageSpider, start_urls=[start_url], page_count=page_count)
    process.start()
