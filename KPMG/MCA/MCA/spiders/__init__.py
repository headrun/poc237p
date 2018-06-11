from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.http import Request, FormRequest
import requests
import re, csv
import datetime
import json

class MCA(Spider):
    name = 'MCA_browse'
    start_urls = []

    def __init__(self, directorname = '', din = '',  **kwargs):
	super(MCA, self).__init__(**kwargs)
	self.directorname = directorname
	self.din = din
	#self.headers = []
        #oupf1 = open('MCA-%s-%s.csv'  % (self.directorname, str(datetime.date.today())), 'wb+')
        #self.csv_file  = csv.writer(oupf1)
        #self.csv_file.writerow(self.headers)

	
    def start_requests(self):
        headers = {
	    'Connection': 'keep-alive',
	    'Upgrade-Insecure-Requests': '1',
	    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
	    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
	    'Accept-Encoding': 'gzip, deflate',
	    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
	}
        yield Request('http://www.mca.gov.in/mcafoportal/dinLookup.do',headers = headers, callback = self.parse)

    def parse(self, response):
	cookie = response.headers.get('Set-Cookie', '')
	cook = {}
        for i in cookie:
            da = i.split(';')[0]
            if da:
                try: key, val = da.split('=', 1)
                except : continue
                cook.update({key.strip():val.strip()})
	
	headers = {
            'Origin': 'http://www.mca.gov.in',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept': '*/*',
            'Referer': 'http://www.mca.gov.in/mcafoportal/showdirectorMasterData.do',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
        }

	cookies = {
            'JSESSIONID':cook.get('JSESSIONID',''),
        }  
	
	data = [
          ('directorName', self.directorname),
          ('fatherLastName', ''),
          ('dob', ''),
        ]

        yield FormRequest('http://www.mca.gov.in/mcafoportal/dinLookup.do', headers=headers, cookies=cookies, formdata=data, method="POST", callback = self.parse_navigate, meta = {'cook':cook})

    def parse_navigate(self, response):
	din_data = json.loads(response.body)
	information = din_data.get('directorList','')
	for info in information:
	    dob = info.get('dob','')
	    din = info.get('din','')

	    fatherLastName = info.get('fatherLastName','')
	    directorName = info.get('directorName','')
	    last_cook = response.meta.get('cook','')
	    cooki = response.headers.get('Set-Cookie', '')
	    cook = {}
	    for i in cooki:
	        da = i.split(';')[0]
	        if da:
		    try: key, val = da.split('=', 1)
		    except : continue
		    cook.update({key.strip():val.strip()})
	    headers = {
		    'Connection': 'keep-alive',
		    'Cache-Control': 'max-age=0',
		    'Origin': 'http://www.mca.gov.in',
		    'Upgrade-Insecure-Requests': '1',
		    'Content-Type': 'application/x-www-form-urlencoded',
		    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
		    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
		    'Referer': 'http://www.mca.gov.in/mcafoportal/showdirectorMasterData.do',
		    'Accept-Encoding': 'gzip, deflate',
		    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
	    }

	    cookies = {
	        'JSESSIONID':cook.get('JSESSIONID',''),
	    }

	    data = [
	  ('directorName', self.directorname),
	  ('din', self.din),
	  ('displayCaptcha', ''),
	  ]

	    yield FormRequest('http://www.mca.gov.in/mcafoportal/showdirectorMasterData.do', headers=headers, cookies=cookies, formdata=data, method = "POST", callback = self.parse_casedetails, meta = {'lat_cook':cook})

    def parse_casedetails(self, response):
	sel = Selector(response)
        din = sel.xpath('//td[contains(text(),"DIN")]/following-sibling::td/text()').extract()
	nodes = sel.xpath('//body//tr')
	for node in nodes:
            cin = ''.join(sel.xpath('.//td[@align="center"]/a//text()').extract()).strip()
	    companynm = ''.join(sel.xpath('.//td[@align="center"][2]//text()').extract()).strip()	
	    import pdb;pdb.set_trace()
	    begindt = ''.join(sel.xpath('/./td[@align="center"][3]//text()').extract()).strip()
	    enddate = ''.join(sel.xpath('.//td[@align="center"][4]//text()').extract()).strip()
	    
	llp_nodes = sel.xpath('//tr[@class="odd"]')
	for node in llp_nodes:
	    llp = ''.join(sel.xpath('.//td[@align="center"]/a//text()').extract()).strip()

	    import pdb;pdb.set_trace()

