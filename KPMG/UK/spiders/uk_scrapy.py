import csv
import re
import datetime

from scrapy.selector import Selector
from scrapy.spiders import Spider
from scrapy.http import Request, FormRequest
import sys  

reload(sys)  
sys.setdefaultencoding('utf8')

headers = {
            'Pragma': 'no-cache',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Referer': 'http://www.bailii.org/uk/cases/UKSC/',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            }


class UKHighCourt(Spider):
	name = 'uk_highcourt'
	start_urls = []

        def __init__(self, prtynme='', *args, **kwargs):
            super(UKHighCourt, self).__init__(**kwargs)
            self.prtynme = prtynme
            self.uk_headers = ['Url', 'Case_id', 'Case_title', 'Appellant', 'Respondent', 'Intervener']
            oupf1 = open('UK-%s-%s.csv'  % (self.prtynme, str(datetime.date.today())), 'wb+')
            self.csv_file  = csv.writer(oupf1)
            self.csv_file.writerow(self.uk_headers)

	def start_requests(self):
		#url = 'http://www.bailii.org/cgi-bin/lucy_search_1.cgi?query=john&results=50&submit=Search&rank=on&callback=on&mask_path=uk%2Fcases%2FUKSC'
		url = 'http://www.bailii.org/cgi-bin/lucy_search_1.cgi?query='+self.prtynme+'&results=50&submit=Search&rank=on&callback=on&mask_path=uk%2Fcases%2FUKSC'
		yield Request(url, callback=self.parse_search, headers=headers)

	def parse_search(self, response):
		sel  = Selector(response)
		headers = {
                'Pragma': 'no-cache',
                'Origin': 'http://www.bailii.org',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Cache-Control': 'no-cache',
                'Referer': response.url,
                'Connection': 'keep-alive',
                        }
		case_urls = sel.xpath('//ol//li//p/a/@href').extract()
		for each_case in case_urls:
			url = 'http://www.bailii.org/' + each_case.strip('/')
			print url
			yield Request(url, self.parse_eachcase, headers=headers)
		rank = ''.join(set(sel.xpath('//input[@type="hidden"][contains(@name, "rank")]/@value').extract()))
		sort = ''.join(set(sel.xpath('//input[@type="hidden"][contains(@name, "sort")]/@value').extract()))
		mask_path = ''.join(set(sel.xpath('//input[@type="hidden"][contains(@name, "mask_path")]/@value').extract()))
		query  = ''.join(set(sel.xpath('//input[@type="hidden"][contains(@name,"query")]/@value').extract()))
		callback = ''.join(set(sel.xpath('//input[@type="hidden"][contains(@name,"callback")]/@value').extract()))
		show = ''.join(set(sel.xpath('//input[@type="hidden"][contains(@name,"show")]/@value').extract()))
		start = ''.join(set(sel.xpath('//input[@type="hidden"][contains(@name, "start")]/@value').extract()))
		submit = ''.join(set(sel.xpath('//form[@action="/cgi-bin/lucy_search_1.cgi"]/input[@type="submit"]/@value').extract()))

		data = [
				  ('rank', rank),
				  ('sort', sort),
				  ('callback', callback),
				  ('query', query),
				  ('mask_path', mask_path),
				  ('show', show),
				  ('show', show),
				  ('start', start),
				]
		yield FormRequest('http://www.bailii.org/cgi-bin/lucy_search_1.cgi', headers=headers, formdata=data, callback=self.parse_search)


	def parse_eachcase(self, response):
		case_title = ','.join(response.xpath('//p[contains(text(), "JUDGMENT")]//following-sibling::blockquote//blockquote/text()').extract()).strip().encode('utf-8')

		if not case_title:
			case_title = ''.join(response.xpath('//b[text()="JUDGMENT"]/../..//following-sibling::p/b/i[text()="v"]/../text()').extract()).strip().encode('utf-8')
			if not case_title:case_title = ','.join(response.xpath('//center//p[@class="Title1"]/span//text()').extract()).strip().encode('utf-8')
			if not case_title: case_title = ','.join(response.xpath('//h2//i[text()="v"]/..//text()').extract()).strip().encode('utf-8')
			if not case_title: case_title = ','.join(response.xpath('//span[@class="font4"]/b/i[text()="v "]/..//text()').extract()).strip().encode('utf-8')
			if not case_title:case_title = ','.join(response.xpath('//blockquote//blockquote/b/text()').extract()).strip().encode('utf-8')
			if not case_title:case_title = ','.join(response.xpath('//ol//center//blockquote//blockquote//text()').extract()).strip().encode('utf-8')
			if not case_title:case_title = ','.join(response.xpath('//center//blockquote//blockquote//b/i[text()="v"]/../text()').extract()).encode('utf-8')
			if not case_title:case_title = ','.join(response.xpath('//center//blockquote//b//i[text()="v"]/../text()').extract()).strip().encode('utf-8')
		appellant  = ','.join(response.xpath('//center//td//i[contains(text(), "Appellant")]/../text()').extract()).encode('utf-8').strip().encode('utf-8').replace('0xc2','')
		appellant = ','.join(response.xpath('//td//i[contains(text(), "Appellant")]/../text()').extract()).encode('utf-8').strip().encode('utf-8').replace('0xc2','')
		if not appellant:
			appellant = ','.join(response.xpath('//table[@class="MsoNormalTable"]//p[@class="MsoNormal"]/i[contains(text(), "Appellant")]/..//following-sibling::p[@class="MsoNormal"]/text()').extract()).strip().encode('utf-8').replace('0xc2','')
			if not appellant:appellant = ','.join(response.xpath('//p[@class="MsoNormal"]/i[text()="Appellant"]/../..//following-sibling::p//i[not(contains(text(), "Appellant"))]//text()').extract()).strip().encode('utf-8').replace('0xc2','')
			if not appellant:
				width  = ''.join(response.xpath('//p[@class="MsoNormal"]/i[text()="Appellant"]/../../@width').extract()).strip().encode('utf-8').replace('0xc2','')
				appellant = ''.join(response.xpath('//td[@width="'+width+'"]//p[@class="MsoNormal"]/text()').extract()).strip().encode('utf-8').replace('0xc2','')

		respondent = ''.join(response.xpath('//center//td//i[contains(text(), "Respondent")]/../text()').extract()).strip().encode('utf-8')
		respondent = ','.join(response.xpath('//td//i[contains(text(), "Respondent")]/../text()').extract()).strip().encode('utf-8')
		if not respondent:
			respondent = ','.join(response.xpath('//table[@class="MsoNormalTable"]//p[@class="MsoNormal"]/i[contains(text(), "Respondent")]/..//following-sibling::p[@class="MsoNormal"]/text()').extract()).strip().encode('utf-8')
			if not respondent:respondent = ','.join(response.xpath('//p[@class="MsoNormal"]/i[text()="Respondent"]/../..//following-sibling::p//i[not(contains(text(), "Respondent"))]//text()').extract()).strip().encode('utf-8')
			if not respondent:
				width  = ''.join(response.xpath('//p[@class="MsoNormal"]/i[text()="Respondent"]/../../@width').extract()).strip().encode('utf-8')
				respondent = ','.join(response.xpath('//td[@width="'+width+'"]//p[@class="MsoNormal"]/text()').extract()).strip().encode('utf-8')
		intervener = ','.join(response.xpath('//center//td//i[contains(text(), "Intervener")]/../text()').extract()).strip().encode('utf-8')
		if not intervener:
			intervener = ','.join(response.xpath('//table[@class="MsoNormalTable"]//p[@class="MsoNormal"]/i[contains(text(), "Intervener")]/..//following-sibling::p[@class="MsoNormal"]/text()').extract()).strip().encode('utf-8')

		case_id = re.findall('/uk/cases/(.*)/(\d+)/(\d+).html', response.url)
		if case_id:case_id = ' '.join(case_id[0])
		values = [response.url, case_id, case_title, appellant, respondent, intervener]
	        self.csv_file.writerow(values)
