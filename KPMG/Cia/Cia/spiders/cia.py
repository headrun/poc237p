import datetime
import os
import csv

from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy.http import Request


class CIAgov(Spider):
    name = 'ciagov'
    start_urls = ['https://www.cia.gov/library/publications/resources/world-leaders-1/']
    count = 0

    def __init__(self):
        self.filename = "ciainfo%s.csv" %(str(datetime.datetime.now().date()))
        self.csv_file = self.is_path_file_name(self.filename)
        self.fields = ["url", "country", "Position", "Leader"]
        self.csv_file.writerow(self.fields)

    def is_path_file_name(self, excel_file_name):
        if os.path.isfile(excel_file_name):
            os.system('rm%s' % excel_file_name)
        oupf = open(excel_file_name, 'ab+')
        todays_excel_file = csv.writer(oupf)
        return todays_excel_file

    def parse(self, response):
        sel = Selector(response)
        total_links = sel.xpath('//div[@id="cosAlphaList"]//@href').extract()
        print total_links
        for each_link in total_links:
            link = "https://www.cia.gov/library/publications/resources/world-leaders-1/" + each_link
            print link
            yield Request(link, callback=self.parse_text)

    def parse_text(self, response):
        sel = Selector(response)
        reference = response.url
        country = sel.xpath('//div[@id="countryOutput"]//td[@class="countryName"]//span//text()').extract()
        containers = response.xpath('//div[@style="page-break-inside: !important;"]')
        for container in containers:
            key = ''.join(container.xpath('.//span[@class="title"]//text()').extract()).strip()
            value = ''.join(container.xpath('.//span[@class="cos_name"]//text()').extract()).strip()
            csv_values = [reference, country, key, value]
            self.csv_file.writerow(csv_values)
