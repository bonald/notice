import scrapy
import requests
import json
import time
from pyquery import PyQuery as pq
from notice.items import SecondBaseNoticeItem
import datetime


def string2datetime(str,format="%Y-%m-%dT%H:%M:%SZ"):
    return datetime.datetime.strptime(str,format)


def utc2local(utc_date):
    now_stamp = time.time()
    local_time = datetime.datetime.fromtimestamp(now_stamp)
    utc_time = datetime.datetime.utcfromtimestamp(now_stamp)
    offset = local_time - utc_time
    res_time = string2datetime(utc_date) + offset
    print(res_time)
    return res_time


class BinanceSpider(scrapy.Spider):
    name = 'binance.com'
    base_url = 'https://support.binance.com'
    notice_url = 'https://support.binance.com/hc/zh-cn/sections/115000202591-%E6%9C%80%E6%96%B0%E5%85%AC%E5%91%8A'

    def start_requests(self, ):

        yield scrapy.Request(url=self.notice_url,
                             dont_filter=True,
                             callback=self.parse_notice)

    def parse_notice(self, response):
        doc = pq(response.body.decode('utf8'))
        notice = list(doc('.article-list li').items())[0]
        detail_url = notice('a').attr('href')
        notice_detail = pq(self.base_url + detail_url)

        item = SecondBaseNoticeItem()
        item['name'] = 'binance'
        item['resource'] = 'binance.com'
        item['url'] = self.base_url + detail_url
        date = notice_detail('.meta-data time').attr('datetime')
        print(date)
        # year, mon, day, hour, minit,second = re.search('(\d+).*?(\d+).*?(\d+).*?(\d+).*?(\d+)', date).groups()

        item['time'] = utc2local(date).strftime("%Y-%m-%d %H:%M:%S")

        item['title'] = notice_detail('.article-title').text().replace('\n', '').replace('\'', '')
        item['main'] = notice_detail('.article-body').text()
        yield item
