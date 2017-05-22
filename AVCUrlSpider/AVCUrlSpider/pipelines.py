# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import  json

from AVCUrlSpider.spiders.SpiderModle import Modle

class AvcurlspiderPipeline(object):
    def process_item(self, item, spider):
        line = json.dumps(dict(item))
        Modle.redis_Server.lpush(Modle.reids_key_wys, line)
