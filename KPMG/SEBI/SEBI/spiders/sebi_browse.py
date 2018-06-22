import datetime
import csv

from scrapy.http     import FormRequest
from scrapy.spider   import BaseSpider
from scrapy.selector import Selector
  
class SEBI(BaseSpider):
    name = 'sebi_browse'
    start_urls = ['https://www.sebi.gov.in/sebiweb/home/cause-list.jsp']

    def __init__(self, search='', dt='', **kwargs):
        super(SEBI, self).__init__(**kwargs)
        self.search = search
        self.dt = dt
        self.headers = ['Hearing/Order Date', 'Proceedings', 'Name of the Entity', 'In the matter of', 'Authority/Bench', 'Timings', 'Previous Hearing Date', 'Office', 'Remarks'] 
        oupf1 = open('SEBI-%s-%s.csv'  % (self.search, str(datetime.date.today())), 'wb+')
        self.csv_file = csv.writer(oupf1) 
        self.csv_file.writerow(self.headers)
  

    def parse(self, response):
        dat1 = response.headers.getlist('Set-cookie')
        cook = {}
        for i in dat1:
            da = i.split(';')[0]
            if da:
                try: key, val = da.split('=', 1)
                except: continue
                cook.update({key.strip():val.strip()})
        cookies = {
            'JSESSIONID':cook.get('JSESSIONID', ''),
        }
        headers = {
	           'Origin': 'https://www.sebi.gov.in',
	           'Accept-Encoding': 'gzip, deflate, br',
	           'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
	           'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
	           'Content-type': 'application/x-www-form-urlencoded',
	           'Accept': '*/*',
	           'Connection': 'keep-alive',
	       }
        data = [
	           ('dt', ''),
	           ('search', self.search),
	       ]

        yield FormRequest('https://www.sebi.gov.in/sebiweb/ajax/home/bydate.jsp', headers=headers, cookies=cookies, formdata=data, callback=self.parse_next)

    def parse_next(self, response):
        sel = Selector(response)
        nodes = sel.xpath('//table[@class="table table-striped table-bordered table-hover"]//tbody/tr')
        for node in nodes:
            order_date = ''.join(node.xpath('.//td[1]//text()').extract()).strip()
            proceedings = ''.join(node.xpath('.//td[2]//text()').extract()).strip() 
            nameofentity = ''.join(node.xpath('.//td[3]//text()').extract()).strip()
            inmatter = ''.join(node.xpath('.//td[4]//text()').extract()).strip()
            authoruty = ''.join(node.xpath('.//td[5]//text()').extract()).strip()
            timings = ''.join(node.xpath('.//td[6]//text()').extract()).strip()
            hearing_date = ''.join(node.xpath('.//td[7]//text()').extract()).strip()
            office = ''.join(node.xpath('.//td[8]//text()').extract()).strip()
            remarks = ''.join(node.xpath('.//td[9]//text()').extract()).strip()
            values = [order_date, proceedings, nameofentity, inmatter, authoruty, timings, hearing_date, office, remarks]
            self.csv_file.writerow(values)
