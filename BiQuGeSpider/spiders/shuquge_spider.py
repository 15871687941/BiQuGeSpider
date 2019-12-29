# -*- coding: utf-8 -*-
import scrapy
from BiQuGeSpider.items import BiqugespiderItem
from copy import deepcopy
import re
import json


class ShuqugeSpiderSpider(scrapy.Spider):
    name = 'shuquge_spider'
    allowed_domains = ['www.shuquge.com']
    start_urls = ['http://www.shuquge.com', ]

    def parse(self, response):
        links = response.css("div.nav>ul>li>a")[1:8]
        for link in links:
            item = BiqugespiderItem()
            url = link.xpath("./@href").get()
            item["bookCategory"] = link.xpath("./text()").get()
            print(item["bookCategory"], url)
            yield scrapy.Request(url=url, callback=self.parse_cat_page, meta={"item": item})

    def parse_cat_page(self, response):
        links = response.css("div.l span.s2 a")
        item = response.meta["item"]
        for link in links:
            item = deepcopy(item)
            url = link.xpath("./@href").get()
            item["bookName"] = link.xpath("./text()").get().strip()
            yield scrapy.Request(url=url, callback=self.parse_item, meta={"item": item})
        nextPage = response.css("ul div.wrap>a")[-2]
        next_page_text = nextPage.xpath("./text()").get()
        if next_page_text == "下一页":
            next_page_url = "http://www.shuquge.com" + nextPage.xpath("./@href").get()
            print(next_page_url)
            scrapy.Request(url=next_page_url, callback=self.parse_cat_page, meta={"item": item})

    def parse_item(self, response):
        item = response.meta["item"]
        info = response.css("div.info div.small>span")
        try:
            item["bookAuthor"] = info.xpath("./text()").re(r"作者：(.*)")[0]
        except:
            item["bookAuthor"] = ""
        try:
            item["bookStatus"] = info.xpath("./text()").re(r"状态：(.*)")[0]
        except:
            item["bookStatus"] = ""
        try:
            item["bookWordCount"] = info.xpath("./text()").re(r"字数：(.*)")[0]
        except:
            item["bookWordCount"] = ""
            
        chapter_url = set()
        links = response.css("div.listmain dl dd>a")
        base_url = re.match(r"(.*)index.html$", response.url).groups()[0]
        for link in links:
            url = base_url + link.xpath("./@href").get()
            chapter = link.xpath("./text()").get()
            chapter_url.add((chapter, url))
        item["chapterNameUrl"] = chapter_url
        return item


