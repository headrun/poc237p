import re
import time
import json
import urllib
import requests
import csv
import sys
import datetime

from scrapy.http     import  Request, FormRequest
from scrapy.spider   import BaseSpider
from scrapy.selector import Selector
  
class RHC(BaseSpider):
    name = 'rajashighcourt_browse'
    start_urls = ['http://rhccasestatus.raj.nic.in/rhcpcis/']

    def __init__(self, partyname = '',**kwargs):
        super(RHC, self).__init__(**kwargs)
        self.partyname = partyname
	self.headers = ['Sr.No.', 'Case Details', 'Party Details', 'Advocate Details' ] 
        oupf1 = open('RHC-%s-%s.csv'  % (self.partyname, str(datetime.date.today())), 'wb+')
        self.csv_file  = csv.writer(oupf1) 
        self.csv_file.writerow(self.headers)
  
    def parse(self, response): 
	dat1 = response.headers.getlist('Set-cookie')
        cook = {}
        for i in dat1:
            da = i.split(';')[0]
            if da:
                try: key, val = da.split('=', 1)
                except : continue
                cook.update({key.strip():val.strip()})
        headers = {
	    'Connection': 'keep-alive',
	    'Upgrade-Insecure-Requests': '1',
	    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
	    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
	    'Referer': 'http://rhccasestatus.raj.nic.in/rhcpcis/sidemenu.asp',
	    'Accept-Encoding': 'gzip, deflate',
	    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
	}
        cookies = {
            'ASPSESSIONIDQQCQRABS':cook.get('ASPSESSIONIDQQCQRABS',''),
        }
	yield Request('http://rhccasestatus.raj.nic.in/rhcpcis/kquarylobisparty.asp', headers=headers, cookies=cookies, callback = self.parse_next, meta = {'cook':cook} )

    def parse_next(self, response):
	new_cook = response.meta.get('cook','')
	cookies = { 'ASPSESSIONIDQQCQRABS':new_cook.get('ASPSESSIONIDQQCQRABS','')}
	headers = {
	    'Connection': 'keep-alive',
	    'Cache-Control': 'max-age=0',
	    'Origin': 'http://rhccasestatus.raj.nic.in',
	    'Upgrade-Insecure-Requests': '1',
	    'Content-Type': 'application/x-www-form-urlencoded',
	    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
	    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
	    'Referer': 'http://rhccasestatus.raj.nic.in/rhcpcis/kquarylobisparty.asp',
	    'Accept-Encoding': 'gzip, deflate',
	    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
	}

	data = [
	  ('txtparty', self.partyname),
	  ('optapr', 'A'),
	  ('txtyear', '2018'),
	  ('submit', 'Get Data'),
	]

	yield FormRequest('http://rhccasestatus.raj.nic.in/rhcpcis/kquarylobisparty.asp?id=get', headers=headers, cookies=cookies, formdata=data, method="POST", meta = {'allow_redirects':False}, callback = self.parse_data)

    def parse_data(self, response):
	sel = Selector(response)
	nodes = sel.xpath('//table[@border="1"]//tr')
	for node in nodes:
	    srno = ''.join(node.xpath('.//td[1]//text()').extract()).strip()
	    case = ''.join(node.xpath('.//td[2]//text()').extract()).strip()
	    party_details = ''.join(node.xpath('.//td[3]//text()').extract()).strip()
	    advocate_details = ''.join(node.xpath('.//td[4]//text()').extract()).strip()
            values = [srno, case, party_details, advocate_details]
	    self.csv_file.writerow(values)
