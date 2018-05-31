import re
import json
import urllib
import requests
import datetime
import csv

from scrapy.http     import  Request, FormRequest
from scrapy.spider   import BaseSpider
from scrapy.selector import Selector
  
class ACOI(BaseSpider):
    name = 'ACOI_browse'
    start_urls = ['http://hc.tap.nic.in/csis/PartyDetails.jsp']

    def __init__(self, prtynme= '', prtype = '', year = '', **kwargs):
        super(ACOI, self).__init__(**kwargs)
        self.prtynme = prtynme
        self.prtype = prtype
        self.year = year
        self.headers = ['Petitioner', 'Respondent', 'PET.ADV', 'RESP.ADV', 'SUBJECT', 'DISTRICT', 'FILING DATE','REG.DATE', 'STATUS']
        #oupf1 = open('ACOI.csv', 'wb+') 
        oupf1 = open('APHC-%s-%s-%s.csv'  % (self.prtynme,self.year, str(datetime.date.today())), 'wb+')
        self.csv_file  = csv.writer(oupf1) 
        self.csv_file.writerow(self.headers)
  
    def parse(self, response):
	sel = Selector(response)
        my_dict = response.headers
        cookies = {}
        i =  my_dict.get('Set-Cookie', '')
        key_ = i
        data = i.split(';')[0]
        if data:
            try : key, val = data.split('=', 1)
            except:
                    pass
            cookies.update({key.strip():val.strip()}) 
 

	headers = {
	    'Pragma': 'no-cache',
	    'Origin': 'http://hc.tap.nic.in',
	    'Accept-Encoding': 'gzip, deflate',
	    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
	    'Upgrade-Insecure-Requests': '1',
	    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36',
	    'Content-Type': 'application/x-www-form-urlencoded',
	    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
	    'Cache-Control': 'no-cache',
	    'Referer': 'http://hc.tap.nic.in/csis/PartyDetails.jsp',
	    'Connection': 'keep-alive',
	}

        sdata = [
            ('prtynme', self.prtynme.upper()),
            ('prtype', 'U'),
            ('year', self.year),
        ]
        sdata = {'prtynme':self.prtynme.upper(), 'prtype':'U', 'year':self.year}
        yield FormRequest('http://hc.tap.nic.in/csis/Partyinfo.jsp', headers =headers, cookies=cookies,  formdata=sdata, callback= self.parse_next)
	
    def parse_next(self, response): 
        sel = Selector(response)
        nodes = sel.xpath('//td[@width=\'20%\']')
        for node in nodes:
	    case_numbr = ''.join(node.xpath('.//a[contains(@href, "MainInfo")]//text()').extract())
	    case_info_url = ''.join(node.xpath('.//a/@href').extract())
            info_url = 'http://hc.tap.nic.in/csis/' + case_info_url
            yield Request(info_url, callback = self.parse_new)

    def parse_new(self, response):
        sel = Selector(response)
 	petitioner = ''.join(sel.xpath('//table[@cellpadding=1]//tr//td[@height=\'50%\'][1]//text()').extract()).strip()
	respondent = ''.join(sel.xpath('//table[@cellpadding=1]//tr//td[@height=\'50%\'][2]//text()').extract()).strip()
        pet = ''.join(sel.xpath('//table[@cellpadding=1]//tr//td//b[contains(text(), "PET.ADV")]/..//following-sibling::font//text()').extract()).strip()
	resp = ''.join(sel.xpath('//table[@cellpadding=1]//tr//td//b[contains(text(), "RESP.ADV")]/..//following-sibling::font/b/text()').extract()).strip()
        subject = ''.join(sel.xpath('//table[@cellpadding=1]//tr//td//b[contains(text(), "SUBJECT")]/..//following-sibling::font/b/text()').extract()).strip()
        district = ''.join(sel.xpath('//table[@cellpadding=1]//tr//td//b[contains(text(), "DISTRICT")]/..//following-sibling::font/b/text()').extract()).strip()
        filing_date = ''.join(sel.xpath('//td//b[contains(text(), "FILING DATE")]/..//following-sibling::font//text()').extract()).strip()
	reg_date = ''.join(sel.xpath('//td//b[contains(text(), "REG. DATE")]/..//following-sibling::font//text()').extract()).strip()
	status = ''.join(sel.xpath('//td//b[contains(text(), "STATUS")]/..//following-sibling::font//text()').extract()).strip()
        values = [petitioner, respondent, pet, resp, subject, district, filing_date, reg_date, status]
        self.csv_file.writerow(values)









