from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy.http import Request, FormRequest
import re
import random
import csv

DEFAULT_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Connection': 'keep-alive',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
}
def extract_data(sel, xpath_, delim=''):
    return delim.join(sel.xpath(xpath_).extract()).strip()

class PatnaHighCourt(Spider):
    name = 'patna_highcourt'
    start_urls = []


    def __init__(self, *args, **kwargs):
        self.keyword = kwargs.get('keyword', '')
        self.year = kwargs.get('year', '')
        self.excel_file_name = 'patna_data_'+self.keyword.replace(' ', '_')+'_'+self.year.strip()+'.csv'
        self.oupf = open(self.excel_file_name, 'w+')
        self.todays_excel_file = csv.writer(self.oupf) 
	court_headers = ['Token Number', 'Status', 'Petitioner', 'Respondent', 'Date of Filing', 'Case Number']
        self.todays_excel_file.writerow(court_headers) 
    def start_requests(self):
        url  = 'http://patnahighcourt.gov.in/CaseSeachByName.aspx'
        yield Request(url, callback=self.parse, headers=DEFAULT_HEADERS)
    def parse(self, response):
        sel = Selector(response)
    	cookie = response.headers.getlist('Set-Cookie')
        cookies = {}
        for i in cookie:
            data = i.split(';')[0]
            if data:
                try: key, val = data.split('=', 1)
                except : continue
                cookies.update({key.strip():val.strip()})
       	headers = {
			'Origin': 'http://patnahighcourt.gov.in',
			'Accept-Encoding': 'gzip, deflate',
			'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
			'Upgrade-Insecure-Requests': '1',
			'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
			'Content-Type': 'application/x-www-form-urlencoded',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
			'Cache-Control': 'max-age=0',
			'Referer': 'http://patnahighcourt.gov.in/CaseSeachByName.aspx',
			'Connection': 'keep-alive',
		}
 			
        event_target = extract_data(sel, '//input[@name="__EVENTTARGET"]/@value')
        event_argument = extract_data(sel, '//input[@name="__EVENTARGUMENT"]/@value')
        view_state = extract_data(sel, '//input[@name="__VIEWSTATE"]/@value')
        event_validation = extract_data(sel, '//input[@id="__EVENTVALIDATION"]/@value')
        view_state_encrypted = extract_data(sel, '//input[@id="__VIEWSTATEENCRYPTED"]/@value')

        data = [
        ('__EVENTTARGET', event_target),
        ('__EVENTARGUMENT', event_argument),
        ('__VIEWSTATE', view_state),
        ('__SCROLLPOSITIONX', '0'),
        ('__SCROLLPOSITIONY', '0'),
        ('__VIEWSTATEENCRYPTED', view_state_encrypted),
        ('__EVENTVALIDATION', event_validation),
        ('ctl00$MainContent$ddlCaseType', '0'),
        ('ctl00$MainContent$txtName', self.keyword),
        ('ctl00$MainContent$txtYear', str(self.year).strip()),
        ('ctl00$MainContent$txtCaptcha', cookies.get('CaptchaImageText', '')),
        ('ctl00$MainContent$btnSeach', 'Show'),
        ]
        basic_search_url = 'http://patnahighcourt.gov.in/CaseSeachByName.aspx'

        yield FormRequest(basic_search_url, callback=self.parse_results, headers=headers, formdata=data, cookies=cookies, meta={'req_cookie':cookies})

    def parse_results(self, response):
        sel = Selector(response)
        cookies = response.meta.get('req_cookie', {})
        view_state = extract_data(sel, '//input[@id="__VIEWSTATE"]/@value')
        view_state_encrypted = extract_data(sel, '//input[@id="__VIEWSTATEENCRYPTED"]/@value')
        event_validation = extract_data(sel, '//input[@id="__EVENTVALIDATION"]/@value')
      	nodes = sel.xpath('//table[contains(@id, "gvSearch")]//tr')

        for node in nodes:
            case_url = extract_data(node, './/td[1]/a/@href')
            case_year = extract_data(node, './/td[2]/text()')
            token_no = extract_data(node, './/td[3]/text()')
            petitioner_name = extract_data(node, './/td[4]/text()')
            respondent_name = extract_data(node, './/td[5]/text()')
            filing_date = extract_data(node, './/td[6]/text()')
            pet_advocate = extract_data(node, './/span[contains(@id, "Label2")]/text()')

            if case_url:
                    values = re.findall("javascript:__doPostBack\('(.*)','(.*)'\)", case_url)
                    if values:
                            ev_target, ev_argument = values[0]

                            screen_y = random.choice(range(0,100))

                            headers = {
                            'Origin': 'http://patnahighcourt.gov.in',
                            'Accept-Encoding': 'gzip, deflate',
                            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
                            'Upgrade-Insecure-Requests': '1',
                            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                            'Cache-Control': 'max-age=0',
                            'Referer': 'http://patnahighcourt.gov.in/CaseSeachByName.aspx',
                            'Connection': 'keep-alive',
                            }

                            data = [
                            ('__EVENTTARGET', ev_target),
                            ('__EVENTARGUMENT', ev_argument),
                            ('__VIEWSTATE', view_state),
                            ('__SCROLLPOSITIONX', '0'),
                            ('__SCROLLPOSITIONY', '181'),
                            ('__VIEWSTATEENCRYPTED', view_state_encrypted),
                            ('__EVENTVALIDATION', event_validation),
                            ('ctl00$MainContent$ddlCaseType', '0'),
                            ('ctl00$MainContent$txtName', ''),
                            ('ctl00$MainContent$txtYear', ''),
                            ('ctl00$MainContent$txtCaptcha', ''),
                            ]
                            base_url = 'http://patnahighcourt.gov.in/CaseSeachByName.aspx'
                            yield FormRequest(base_url, self.parse_eachcase, headers=headers, formdata=data, cookies=cookies)		


    def parse_eachcase(self, response):
        sel = Selector(response)
        token_number = extract_data(sel, '//table[@class="CSSCaseStatus"]//th[contains(text(), "Token Number")]/..//following-sibling::td/span[contains(@id, "CaseNo")]/text()')
        case_status = extract_data(sel, '//table[@class="CSSCaseStatus"]//th[contains(text(), "Status :")]/..//following-sibling::td/span[contains(@id, "Label5")]/text()')
        petitioner = extract_data(sel, '//table[@class="CSSCaseStatus"]//th[contains(text(), "Petitioner")]/..//following-sibling::td/span[contains(@id, "Label6")]/text()')
        respondent = extract_data(sel, '//table[@class="CSSCaseStatus"]//th[contains(text(), "Respondent")]/..//following-sibling::td/span[contains(@id, "Label3")]/text()')
        date_filing = extract_data(sel, '//table[@class="CSSCaseStatus"]//th[contains(text(), "Date of Filing")]/..//following-sibling::td/span[contains(@id, "Label1")]/text()')
        case_no = extract_data(sel, '//table[@class="CSSCaseStatus"]//th[contains(text(), "Case No.")]/..//following-sibling::td//a[contains(@id, "HyperLink")]/text()')
	values = [token_number, case_status, petitioner, respondent, date_filing, case_no]
	self.todays_excel_file.writerow(values)
