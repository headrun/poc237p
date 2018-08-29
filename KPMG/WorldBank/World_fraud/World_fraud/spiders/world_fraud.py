from scrapy.spider import BaseSpider
from scrapy.http import Request
from scrapy.selector import Selector
import csv
import datetime

import sys

reload(sys)
sys.setdefaultencoding('utf8')

class WorldBank(BaseSpider):
	name = "world_fraud"
	start_urls = []

    	def __init__(self, *args, **kwargs):
        	self.keyword = kwargs.get('keyword', '')
		self.headers = ['Name', 'Address', 'Country', 'Period From', 'Period To', 'Grounds']
        	oupf1 = open('World_fraud-%s-%s.csv'  % (self.keyword, str(datetime.date.today())), 'wb+')
        	self.csv_file  = csv.writer(oupf1) 
        	self.csv_file.writerow(self.headers)
  
		court_headers = ['Name', 'Address', 'Country', 'Period From', 'Period To', 'Grounds']

	def start_requests(self):
		#url = 'http://web.worldbank.org/external/default/main?pagePK=64148989&piPK=64148984&theSitePK=84266&theSitePK=84266&contentMDK=64069844&querycontentMDK=64069700&sup_name=MARK&supp_country='
		url = 'http://web.worldbank.org/external/default/main?pagePK=64148989&piPK=64148984&theSitePK=84266&theSitePK=84266&contentMDK=64069844&querycontentMDK=64069700&sup_name='+self.keyword+'&supp_country='
		yield Request(url, callback=self.parse)

	def parse(self, response):
		sel = Selector(response)
		#nodes = sel.xpath('//table[@summary="List of Debarred Firms"]//tr')
		nodes =  sel.xpath('//table[@summary="List of Debarred Firms"]/script//following-sibling::tr')
		for node in nodes:
			first_name = ''.join(node.xpath('./td[1]//text()').extract())
			address = ''.join(node.xpath('./td[2]//text()').extract())
			country = ''.join(node.xpath('./td[3]//text()').extract())
			period_from = ''.join(node.xpath('./td[4]//text()').extract())
			period_to = ''.join(node.xpath('./td[5]//text()').extract())
			grounds = ''.join(node.xpath('./td[6]//text()').extract())
			values = [first_name, address, country, period_from, period_to, grounds]
			self.csv_file.writerow(values)
