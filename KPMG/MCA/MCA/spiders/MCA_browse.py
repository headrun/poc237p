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

    def __init__(self, directorname = '', **kwargs):
	super(MCA, self).__init__(**kwargs)
	self.directorname = directorname
	self.headers1 = ['Director Name','DIN','CIN/FCRN','Company Name','Begin Date','End Date']
        self.headers2 = ['Director name','DIN','LLPIN/FLLPIN','LLP Name','Begin Date','End Date']
	
        oupf1 = open('MCA1-%s-%s.csv'  % (self.directorname, str(datetime.date.today())), 'wb+')
        oupf2 = open('MCA2-%s-%s.csv'  % (self.directorname, str(datetime.date.today())), 'wb+')
        self.csv_file_1 = csv.writer(oupf1)
        self.csv_file_2  = csv.writer(oupf2)
        self.csv_file_1.writerow(self.headers1)
        self.csv_file_2.writerow(self.headers2)

	
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
	  ('directorName', directorName),
	  ('din', din),
	  ('displayCaptcha', ''),
	  ]
            print directorName
            print din
            yield FormRequest('http://www.mca.gov.in/mcafoportal/showdirectorMasterData.do', headers=headers, cookies=cookies, formdata=data, method = "POST", callback = self.parse_casedetails, meta = {'lat_cook':cook, 'dirnam': directorName, 'din':din})

    def parse_casedetails(self, response):
        dirtrnm = response.meta.get('dirnam','')
        din = response.meta.get('din','')
	sel = Selector(response)
        din = ''.join(sel.xpath('//td[contains(text(),"DIN")]/following-sibling::td/text()').extract()).strip()
	nodes = sel.xpath('//*[@id="companyData"]/tr')
	for node in nodes:
            cin = ''.join(node.xpath('./td/a//text()').extract()).strip()
	    companynm = ''.join(node.xpath('./td[2]//text()').extract()).strip()
	    begindt = ''.join(node.xpath('./td[3]//text()').extract()).strip()
	    enddate = ''.join(node.xpath('./td[4]//text()').extract()).strip()
	    cvalues = [dirtrnm, din, cin, companynm, begindt, enddate]
	    self.csv_file_1.writerow(cvalues)

        llp_nodes = sel.xpath('//*[@id="llpData"]/tr')
        for node in llp_nodes:
            llp = ''.join(node.xpath('./td/a//text()').extract()).strip()
            llpnm = ''.join(node.xpath('./td[2]//text()').extract()).strip()
            begindt = ''.join(node.xpath('./td[3]//text()').extract()).strip()
            enddt = ''.join(node.xpath('./td[4]//text()').extract()).strip()
            lvalues = [dirtrnm, din, llp, llpnm, begindt, enddt]
            self.csv_file_2.writerow(lvalues)
