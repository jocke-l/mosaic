import os
import urllib.parse
from uuid import uuid4

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.loader import ItemLoader
from scrapy.pipelines.files import S3FilesStore, FSFilesStore
from scrapy.pipelines.images import ImagesPipeline

from mosaic.dominant_color import get_dominant_color

BASE_URL = 'https://www.google.se'


class DuplicateFSFilesStore(FSFilesStore):
    def _get_filesystem_path(self, path):
        *parts, filename = path.split('/')
        return super()._get_filesystem_path(
            os.path.join(*parts, '{}_{}'.format(uuid4(), filename))
        )


class DominantColorImagesPipeline(ImagesPipeline):
    STORE_SCHEMES = {
        '': DuplicateFSFilesStore,
        'file': DuplicateFSFilesStore,
        's3': S3FilesStore,
    }

    def get_images(self, response, request, info):
        path, image, buf = next(super().get_images(response, request, info))
        yield '{}.jpg'.format(get_dominant_color(image)), image, buf


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
        'ITEM_PIPELINES': {'mosaic.collector.DominantColorImagesPipeline': 1},
        'IMAGES_STORE': data_dir,
        'COOKIES_ENABLED': False
    })

    start_url = BASE_URL + '/search?' + urllib.parse.urlencode(
        {'q': ' '.join(keywords),
         'tbm': 'isch'}
    )
    process.crawl(ImageSpider, start_urls=[start_url], page_count=page_count)
    process.start()
