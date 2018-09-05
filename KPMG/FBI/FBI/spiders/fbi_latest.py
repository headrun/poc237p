import datetime
import os
import csv
import re
import math

from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy.http import Request
import sys

reload(sys)
sys.setdefaultencoding('utf8')

class FBI(Spider):
    name = 'fbi_latest'
    start_urls = ['https://www.fbi.gov/wanted']

    def __init__(self):
        self.filename = "fbi%s.csv" %(str(datetime.datetime.now().date()))
        self.csv_file = self.is_path_file_name(self.filename)
        self.fields = ["Name", "URL", "Alias", "Remarks", "Caution" ]
        self.csv_file.writerow(self.fields)

    def is_path_file_name(self, excel_file_name):
        if os.path.isfile(excel_file_name):
            os.system('rm%s' % excel_file_name)
        oupf = open(excel_file_name, 'ab+')
        todays_excel_file = csv.writer(oupf)
        return todays_excel_file

    def parse(self, response):
                sel = Selector(response)
                category_urls = sel.xpath('//ul[@class="inline-list section-menu"]//li//a//@href').extract()
                for each in category_urls:
                        yield Request(each, callback = self.parse_next)

    def parse_next(self, response):
                sel = Selector(response)
                url = response.url
		if 'terrorism' in url:
			per_page_results = sel.xpath('//p[@class="read-more text-center bottom-total visualClear"]/text()').extract()
                        data = re.findall('\d+', per_page_results[0])
                        total_pages = data[2]
                        results_per_page = data[1]
                        page_number = float(total_pages)/float(results_per_page)
                        no_of_pages = int(math.ceil(page_number))
                        for_need = no_of_pages + 1
                        y = range(1,for_need)
                        complete_url = "https://www.fbi.gov/wanted/terrorism/@@castle.cms.querylisting/55d8265003c84ff2a7688d7acd8ebd5a?page="
                        for x in y:
                                terroism_url = complete_url+str(x)
                                yield Request(terroism_url, callback=self.parse_allnames)

		if 'vicap' in url:
                        per_page_results = sel.xpath('//p[@class="read-more text-center bottom-total visualClear"]/text()').extract()
                        data = re.findall('\d+', per_page_results[0])
                        total_pages = data[2]
                        results_per_page = data[1]
                        page_number = float(total_pages)/float(results_per_page)
                        no_of_pages = int(math.ceil(page_number))
                        for_need = no_of_pages + 1
                        y = range(1,for_need)
                        complete_url = "https://www.fbi.gov/wanted/vicap/@@castle.cms.querylisting/querylisting-1?page="
                        for x in y:
                                seeking_url = complete_url+str(x)
                                yield Request(seeking_url, callback=self.parse_allnames)

		if 'seeking-information' in url:
                        per_page_results = sel.xpath('//p[@class="read-more text-center bottom-total visualClear"]/text()').extract()
                        data = re.findall('\d+', per_page_results[0])
                        total_pages = data[2]
                        results_per_page = data[1]
                        page_number = float(total_pages)/float(results_per_page)
                        no_of_pages = int(math.ceil(page_number))
                        for_need = no_of_pages + 1
                        y = range(1,for_need)
                        complete_url = "https://www.fbi.gov/wanted/seeking-information/@@castle.cms.querylisting/5abe9de716674277b799bc03b34e1aa4?page="
                        for x in y:
                                seeking_url = complete_url+str(x)
                                yield Request(seeking_url, callback=self.parse_allnames)

		if 'wanted/kidnap' in url:
                        per_page_results = sel.xpath('//p[@class="read-more text-center bottom-total visualClear"]/text()').extract()
                        data = re.findall('\d+', per_page_results[0])
                        total_pages = data[2]
                        results_per_page = data[1]
                        page_number = float(total_pages)/float(results_per_page)
                        no_of_pages = int(math.ceil(page_number))
                        for_need = no_of_pages + 1
                        y = range(1,for_need)
                        complete_url = "https://www.fbi.gov/wanted/kidnap/@@castle.cms.querylisting/querylisting-1?page="
                        for x in y:
                                kidnap_url = complete_url+str(x)
                                yield Request(kidnap_url, callback=self.parse_allnames)

		if 'topten' in url:
                        name_url_nodes = sel.xpath('//div[@id="query-results-0f737222c5054a81a120bce207b0446a"]//ul//li')
                        for node in name_url_nodes:
                                name = ''.join(node.xpath('./h3/a//text()').extract())
                                print name
                                each_url = ''.join(node.xpath('./h3/a/@href').extract())
                                print each_url
                                yield Request(each_url, callback=self.parse_detail, meta = {'name':name})
		
		if 'fugitives' in url:
                        per_page_results = sel.xpath('//p[@class="read-more text-center bottom-total visualClear"]/text()').extract()
                        data = re.findall('\d+', per_page_results[0])
                        total_pages = data[2]
                        results_per_page = data[1]
                        page_number = float(total_pages)/float(results_per_page)
                        no_of_pages = int(math.ceil(page_number))
                        for_need = no_of_pages + 1
                        y = range(1,for_need)
                        complete_url = "https://www.fbi.gov/wanted/fugitives/@@castle.cms.querylisting/f7f80a1681ac41a08266bd0920c9d9d8?page="
                        for x in y:
                                fugitives_url = complete_url+str(x)
                                yield Request(fugitives_url, callback=self.parse_allnames)

		if 'parental-kidnappings' in url:
                        name_url_nodes = sel.xpath('//div[@id="query-results-querylisting-1"]//ul//li')
                        for node in name_url_nodes:
                                name = ''.join(node.xpath('./h3/a//text()').extract())
                                print name
                                each_url = ''.join(node.xpath('./h3/a/@href').extract())
                                print each_url
                                yield Request(each_url, callback=self.parse_detail, meta = {'name':name})

		if 'bank-robbers' in url:
			name_url_nodes = sel.xpath('//div[@class="query-results pat-pager"]//ul//li')
                	for node in name_url_nodes:
                        	name = ''.join(node.xpath('./p/a//text()').extract())
                        	each_url = ''.join(node.xpath('./p/a/@href').extract())
                        	yield Request(each_url, callback=self.parse_detail,meta = {'name':name})
	
		if 'ecap' in url:
                        name_url_nodes = sel.xpath('//div[@id="query-results-querylisting-1"]//ul//li')
                        for node in name_url_nodes:
                                name = ''.join(node.xpath('./h3/a//text()').extract())
                                print name
                                each_url = ''.join(node.xpath('./h3/a/@href').extract())
                                print each_url
                                yield Request(each_url, callback=self.parse_detail, meta = {'name':name})

    def parse_allnames(self, response):
                sel = Selector(response)
                #name_url_nodes = sel.xpath('//div[@id="query-results-55d8265003c84ff2a7688d7acd8ebd5a"]//ul//li')
		
		name_url_nodes = sel.xpath('//div[@class="query-results pat-pager"]//ul//li')
                for node in name_url_nodes:
                        name = ''.join(node.xpath('./p/a//text()').extract())
			if not name: name = ''.join(node.xpath('./h3/a//text()').extract())
                        print name
                        each_url = ''.join(node.xpath('./p/a/@href').extract())
			if not each_url: each_url = ''.join(node.xpath('./h3/a/@href').extract())
                        print each_url
                        yield Request(each_url, callback=self.parse_detail,meta = {'name':name})

    def parse_detail(self, response):
        name = response.meta.get('name','')
        url = response.url
        sel = Selector(response)
        aliases = ''.join(sel.xpath('//section[@id="content-core"]//div[@class="wanted-person-aliases"]/p//text()').extract())
        remarks = ''.join(sel.xpath('//section[@id="content-core"]//div[@class="wanted-person-remarks"]/p//text()').extract())
        caution = ''.join(sel.xpath('//section[@id="content-core"]//div[@class="wanted-person-caution"]/p//text()').extract())
        csv_values = [name, url, aliases, remarks, caution ]
        self.csv_file.writerow(csv_values)

