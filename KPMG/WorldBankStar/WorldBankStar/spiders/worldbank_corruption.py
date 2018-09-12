from scrapy.spider import BaseSpider
from scrapy.http import Request
from scrapy.selector import Selector
import csv
import datetime
import re
import sys

reload(sys)
sys.setdefaultencoding('utf8')

class WorldBank(BaseSpider):
        name = "world_star"
        start_urls = ['https://star.worldbank.org/corruption-cases/assetrecovery/']

        def __init__(self, *args, **kwargs):
                self.headers = ['Pdf url', 'Case Name', 'Jurisdiction of Settlement', 'Type of Settlement', 'Monetary Sanctions', 'Offenses-Alleged', 'Summary']
                oupf1 = open('world_stars_settlements-%s.csv'  % (str(datetime.date.today())), 'wb+')
                self.csv_file  = csv.writer(oupf1)
                self.csv_file.writerow(self.headers)
		self.headings = ['Pdf url','Case title', 'Jurisdiction of Origin', 'UNCAC Offenses Implicated', 'Money laundering Implicated', 'Legal Basis for Asset Recovery', 'Contributing Factors in Asset Recovery', 'Assets Adjudicated/Not Yet Returned (USD)', 'Case Summary', 'Disposition of Criminal Case(s)']
        	oupf2 = open('world_stars_assets-%s.csv' %(str(datetime.date.today())), 'wb+')
        	self.document_file = csv.writer(oupf2)
        	self.document_file.writerow(self.headings)



        def parse(self, response):
                sel = Selector(response)
		settlements = ''.join(sel.xpath('//section[@id="block-facetapi-60wthpqk1klbiwro0hdjojlrqgsm7zzv"]//ul[@id="facetapi-facet-apachesolrstar-1b-block-bundle"]/li[1]/a/@href').extract())
		if settlements:
			settle_url = 'https://star.worldbank.org' + settlements
			yield Request(settle_url, callback=self.parse_settlements)

		asset_recovery = ''.join(sel.xpath('//section[@id="block-facetapi-60wthpqk1klbiwro0hdjojlrqgsm7zzv"]//ul[@id="facetapi-facet-apachesolrstar-1b-block-bundle"]/li[2]/a/@href').extract())
		if asset_recovery:
			asset_url = 'https://star.worldbank.org' + asset_recovery
			yield Request(asset_url, callback=self.parse_assests)

	def parse_settlements(self, response):	
		sel = Selector(response)
		info_nodes = sel.xpath('//section[@id="block-system-main"]/table[@class="table table-hover"]/tbody//tr')
		for node in info_nodes:
			pdf_url = ''.join(node.xpath('./td/following-sibling::td/a/@href').extract())
			title = ''.join(node.xpath('./td/a//text()').extract()).strip()
			jurisdiction = ''.join(node.xpath('./td[2]//text()').extract()).strip()
			yield Request(pdf_url, callback=self.parse_detailed_information, meta = {'case_name':title, 'jurisdiction':jurisdiction})

		url_paging = ''.join(sel.xpath('//div[@class="col-md-12 col-sm-12 npr npl paginationCont"]//div[@class="col-md-4 col-sm-4 txtRight"]/span[@class="prev"]/following-sibling::span/a/@href').extract())
		if not url_paging: url_paging = ''.join(sel.xpath('//div[@class="col-md-12 col-sm-12 npr npl paginationCont"]//div[@class="col-md-4 col-sm-4 txtRight"]/span/a/@href').extract())
		pagination = 'https://star.worldbank.org/' + url_paging
		yield Request(pagination, callback=self.parse_settlements)

	def parse_detailed_information(self, response):
		url = response.url
		case_name = response.meta.get('case_name','')
		jurisdiction = response.meta.get('jurisdiction','')
		sel = Selector(response)
		info = response.body
		Type_of_Settlement =  ''.join(re.findall('Type of Settlement.* Tf (.*) TJ .*Legal Form of Settlement', info.replace('\n', '')))
		Type_of_Settlement = ''.join(re.findall(r'\((.*?)\)',Type_of_Settlement)) 
		Monetary_Sanctions =  ''.join(re.findall('Monetary Sanctions.* Tf (.*) TJ .*Total Monetary Sanctions', info.replace('\n', '')))
		Monetary_Sanctions = ''.join(re.findall(r'\((.*?)\)',Monetary_Sanctions))
		Offense_alleged = ''.join(re.findall('Offenses - Alleged.* Tf (.*) TJ .*Offenses - Settled', info.replace('\n', '')))
		Offense_alleged = ''.join(re.findall(r'\((.*?)\)',Offense_alleged))
		adsa = ''.join(re.findall('Summary:\xa0\)\](.*)\[\(Sources', info.replace('\n', '')))
		des_list = re.findall('\([^\[\]]*\)', adsa)
		final_desc = ''.join([des.replace('))', ') ').replace('((', ' (').strip('(').strip(')') for des in des_list]).replace('\\','').strip()
		values = [url, case_name, jurisdiction, Type_of_Settlement, Monetary_Sanctions, Offense_alleged, final_desc]
		self.csv_file.writerow(values)


	def parse_assests(self, response):
		sel = Selector(response)
		info_nodes = sel.xpath('//section[@id="block-system-main"]/table[@class="table table-hover"]/tbody//tr')
                for node in info_nodes:
                        pdf_url = ''.join(node.xpath('./td/following-sibling::td/a/@href').extract())
                        title = ''.join(node.xpath('./td/a//text()').extract()).strip()
			jurisdiction = ''.join(node.xpath('./td[3]//text()').extract()).strip()
			yield Request(pdf_url, callback=self.parse_complete_assests,  meta = {'case_name':title, 'jurisdiction':jurisdiction})

		url_paging = ''.join(sel.xpath('//div[@class="col-md-12 col-sm-12 npr npl paginationCont"]//div[@class="col-md-4 col-sm-4 txtRight"]//span[2]/a/@href').extract())
		if not url_paging: url_paging = ''.join(sel.xpath('//div[@class="col-md-12 col-sm-12 npr npl paginationCont"]//div[@class="col-md-4 col-sm-4 txtRight"]/span/a/@href').extract())
                pagination = 'https://star.worldbank.org/' + url_paging
		yield Request(pagination, callback=self.parse_assests)

	def parse_complete_assests(self, response):
		url = response.url
		case_name = response.meta.get('case_name','') 
		jurisdiction = response.meta.get('jurisdiction','')
		assests_info = response.body
		offen = ''.join(re.findall('UNCAC Offenses Implicated:\xa0\)\](.*)\[\(Money laundering Implicated', assests_info.replace('\n', '')))
		Offenses = ''.join(re.findall('\([^\[\]]*\)', offen))
		Offenses = ''.join(re.findall(r'\((.*?)\)',Offenses))
		money_laundering = ''.join(re.findall('Money laundering Implicated:\xa0\)\](.*)\[\(Legal Basis for Asset Recovery', assests_info.replace('\n', ''))) 
		money_laundering = ''.join(re.findall('\([^\[\]]*\)', money_laundering))
		money_laundering = ''.join(re.findall(r'\((.*?)\)',money_laundering))
		legal_basis = ''.join(re.findall('Legal Basis for Asset Recovery:\xa0\)\](.*)\[\(Intl.Cooperation: MLAT/Letter of Request?', assests_info.replace('\n', ''))) 
		legal_basis = ''.join(re.findall('\([^\[\]]*\)', legal_basis))
		legal_basis = ''.join(re.findall(r'\((.*?)\)',legal_basis))
		contri_factors = ''.join(re.findall('Contributing Factors in Asset Recovery:\xa0\)\](.*)\[\(Status of Asset Recovery', assests_info.replace('\n', '')))
		con_list = re.findall('\([^\[\]]*\)', contri_factors)
		factors = ''.join([con.replace('))', ') ').replace('((', ' (').strip('(').strip(')') for con in con_list]).replace('\\','').strip()
		assests_adjudicated = ''.join(re.findall('Assets Adjudicated, Not Yet Returned(.*)Assets Returned', assests_info.replace('\n', '')))
		adjudicated = re.findall('\([^\[\]]*\)', assests_adjudicated)
		final_Adjudicated = ''.join([adj.replace('))', ') ').replace('((', ' (').strip('(').strip(')') for adj in adjudicated]).replace('\\','').strip().replace('USD):\xa0','')
		summary = ''.join(re.findall('Case Summary:\xa0\)\](.*)\[\(Disposition of Criminal Case', assests_info.replace('\n', '')))
		sum_list = re.findall('\([^\[\]]*\)', summary)
		case_summary =''.join([sum.replace('))', ') ').replace('((', ' (').strip('(').strip(')') for sum in sum_list]).replace('\\','').strip()
		invest = ''.join(re.findall('Disposition of Criminal Case(.*)Jurisdiction of Origin: Investigative Agency', assests_info.replace('\n', '')))
		jur_invest = re.findall('\([^\[\]]*\)', invest)
		final_invest = ''.join([jur.replace('))', ') ').replace('((', ' (').strip('(').strip(')') for jur in jur_invest]).replace('\\','').strip().replace('s):\xa0','')
		values = [url, case_name, jurisdiction, Offenses, money_laundering, legal_basis, factors, final_Adjudicated, case_summary, final_invest]
            	self.document_file.writerow(values)
