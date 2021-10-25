import scrapy
from urllib.parse import urlencode
from urllib.parse import urlparse
import json
from datetime import datetime
import pandas as pd
from scrapy.shell import inspect_response
import itertools 

API_KEY = '66bd804b7fecc871be1361593bde26ed'

def get_url(url):
    payload = {'api_key': API_KEY, 'url': url, 'country_code': 'us'}
    proxy_url = 'http://api.scraperapi.com/?' + urlencode(payload)
    return proxy_url


class ScholarSpider(scrapy.Spider):
    name = 'scholar'
    allowed_domains = ['api.scraperapi.com']

    BASE_URL = 'https://scholar.google.com'

    def start_requests(self):
        titles = ['Research trends on Big Data in Marketing: A text mining and topic modeling based literature analysis']
        for title in titles:
            url = 'https://scholar.google.com/scholar?' + urlencode({'hl': 'en', 'q': title})
            yield scrapy.Request(get_url(url), callback=self.parse, meta={'position': 0})
        
        
    def parse(self, response):
         cite = response.xpath("//*[@id='gs_res_ccl_mid']/div/div[2]/div[3]/a[3]").attrib['href']
         cite_url = self.BASE_URL + cite
         yield scrapy.Request(get_url(cite_url), callback = self.parse_cited)
         


    
    def parse_cited(self, response):
        year = response.xpath('//*[@id="gs_res_sb_yyl"]/li[3]/a').attrib['href']
        since_url = self.BASE_URL + year
        yield scrapy.Request(get_url(since_url), callback = self.parse_contents)

        
    
    def parse_contents(self, response):
        results = response.css('div.gs_r.gs_or.gs_scl')
        titles = results.css('h3.gs_rt')
        for (result, title) in zip(results, titles):
            item = {
            'title' : title.css('a::text').get(),
            'link' : result.css('a::attr(href)').get()
            }
            yield item
        
        next_page = response.xpath('//td[@align="left"]/a/@href').extract_first()
        if next_page:
            next_url = self.BASE_URL + next_page
            yield scrapy.Request(get_url(next_url), callback=self.parse_contents)
