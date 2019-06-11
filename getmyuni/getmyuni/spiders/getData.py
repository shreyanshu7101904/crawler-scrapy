import scrapy
import json

class GetData(scrapy.Spider):
    name = "geturldata"
    def start_requests(self):
        urls = 'https://www.getmyuni.com/engineering-colleges'
 
        yield scrapy.Request(url=urls, callback=self.parse)

    def parse(self, response):
        print(response.body)
