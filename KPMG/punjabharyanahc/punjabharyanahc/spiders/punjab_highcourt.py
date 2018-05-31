from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.http import Request, FormRequest
import requests
import re, csv
import datetime

class PunjabHaryanaSpider(Spider):
	name = 'punjab_hc'
	start_urls = []
	def __init__(self, *args, **kwargs):
		self.word = kwargs.get('keyword', '')
		self.from_date = kwargs.get('from_date', '')
		self.to_date = kwargs.get('to_date', '')
		self.path = kwargs.get('path', '')	
		self.excel_file_name = self.path+'/'+ '%s_%s_%s_hc_punjab-haryana_%s.csv'%(self.word.replace(' ', '-'), self.from_date.replace('/','-'), self.to_date.replace('/','-'), datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d').replace(' ', '_'))
		self.oupf = open(self.excel_file_name, 'wb+')	
		self.todays_excel_file = csv.writer(self.oupf) 
		court_headers = ['Case ID', 'Petitioner Name', 'Respondent Name', 'Advocate Name', 'Status', 'Next Date', 'Diary Number', 'District', 'Category', 'Main Case Detail', 'Party Detail', 'List Type']
		self.todays_excel_file.writerow(court_headers)	
		self.headers = {
            		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            		'Connection': 'keep-alive',
            		'Accept-Encoding': 'gzip, deflate, br',
            		'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            		'Upgrade-Insecure-Requests': '1',
            		'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
        		}
	
	
	def start_requests(self):
		url =  'https://phhc.gov.in/home.php?search_param=pname'	
		yield Request(url, callback=self.parse, headers=self.headers)


	def parse(self, response):
		cookie = response.headers.get('Set-Cookie', '')
		session_id = ''.join(re.findall('PHPSESSID=(.*);', cookie))
		req_cookie = {'PHPSESSID':session_id}
		headers = self.headers
		headers['Referer'] = 'https://phhc.gov.in/home.php?search_param=pname'
		payload = {'pet_name':(None, self.word), 'pet_or_res':(None, ''), 'date_from':(None, self.from_date), 'date_to':(None, self.to_date), 't_case_type':(None, ''), 't_case_year':(None, ''), 't_case_dist':(None, ''), 'submit':(None, 'Search Case')}
		response = requests.post('https://phhc.gov.in/home.php?search_param=pname', headers=headers, cookies=req_cookie, files=payload)
		sel = Selector(text=response.text)
		nodes = sel.xpath('//table[@id="tables11"]//tr[contains(@class, "alt")]')
		for each in nodes:
			case_url = ''.join(each.xpath('./td//@href').extract())
			list_ = each.xpath('./td//text()').extract()
			complete_url  = "https://phhc.gov.in/"+ case_url.strip()
			yield Request(complete_url, callback=self.parse_casedetails, meta={'details':list_}, headers=self.headers)

		next_url = ''.join(sel.xpath('//a[contains(text(), "next")]/@href').extract()).strip('.').strip()
		if next_url:complete_next_url  = 'https://phhc.gov.in'+next_url
		else:complete_next_url = ''
		cookies = req_cookie
		headers = self.headers
		headers['Referer'] = 'https://phhc.gov.in/home.php?search_param=pname'	
		if complete_next_url:
			yield Request(complete_next_url, self.parse_navigate, headers=headers, cookies=cookies, meta={'req_cookie':cookies})


	def parse_navigate(self, response):
		sel = Selector(response)
		nodes = sel.xpath('//table[@id="tables11"]//tr[contains(@class, "alt")]')
		for each in nodes:
			case_url = ''.join(each.xpath('./td//@href').extract())
			list_ = each.xpath('./td//text()').extract()
			complete_url  = "https://phhc.gov.in/"+ case_url.strip()
			yield Request(complete_url, callback=self.parse_casedetails, meta={'details':list_}, headers=self.headers)

		next_url = ''.join(sel.xpath('//a[contains(text(), "next")]/@href').extract()).strip('.').strip()
		if next_url:complete_next_url  = 'https://phhc.gov.in'+next_url
		else:complete_next_url = ''
		cookies = response.meta.get('req_cookie', {})
		
		headers = self.headers
		headers['Referer'] = 'https://phhc.gov.in/home.php?search_param=pname'
		if complete_next_url:
			yield Request(complete_next_url, self.parse_navigate, headers=headers, cookies=cookies, meta={'req_cookie':cookies})



		
	def parse_casedetails(self, response):
		prev_case_details = response.meta.get('details', [])
		diary_number 		= ''.join(response.xpath('//td[contains(text(), "Diary Number")]/following-sibling::td[@class="data_item"][1]/text()').extract()).strip()
		district 			= ''.join(response.xpath('//td[contains(text(), "District")]/following-sibling::td[@class="data_item"][1]/text()').extract()).strip()
		category 			= ''.join(response.xpath('//td[contains(text(), "Category")]/following-sibling::td[@class="data_item"][1]/text()').extract()).strip()
		status 				= ''.join(response.xpath('//td[contains(text(), "Status ")]/following-sibling::td[@class="data_item"][1]/text()').extract()).strip()
		main_case_detail 	= ''.join(response.xpath('//td[contains(text(), "Main Case Detail")]/following-sibling::td[@class="data_item"][1]/text()').extract()).strip()
		party_detail 		= ''.join(response.xpath('//td[contains(text(), "Party Detail")]/following-sibling::td[@class="data_item"][1]/text()').extract()).strip()
		adv_name 			= ''.join(response.xpath('//td[contains(text(), "Advocate Name")]/following-sibling::td[@class="data_item"][1]/text()').extract()).strip()
		list_type 			= ''.join(response.xpath('//td[contains(text(), "List Type")]/following-sibling::td[@class="data_item"][1]/text()').extract()).strip()
		
		next_date           = response.xpath('//td[contains(text(), "Next date ")]/following-sibling::td[contains(@class, "date")]//text()').extract()
		fir_details  		=  response.xpath('//th[contains(text(), "FIR Details")]/../following-sibling::tr[2]//td[@class="data_sub_item"]/text()').extract()
		
		values = prev_case_details
		values[3] = adv_name
		values[4] = status
		values.extend([diary_number, district, category, main_case_detail, party_detail, list_type])
		self.todays_excel_file.writerow(values)
