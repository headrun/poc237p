''' This script is reilated to interpol it disobeys the robots.txt
'''
import datetime
import os
import csv
from scrapy.http import FormRequest, Request
from scrapy.selector import Selector
from scrapy.spiders import BaseSpider
class Interpol(BaseSpider):
    '''
    class starts
    '''
    name = 'interpol'
    start_domain = ['https://www.interpol.int']
    start_urls = ['https://www.interpol.int/notice/search/wanted']

    def __init__(self, keyword = '', *args, **kwargs):
        super(Interpol, self).__init__(*args, **kwargs)
        self.keyword = keyword
	self.filename = "interpol%s.csv" % (str(datetime.datetime.now().date()))
        self.csv_file = self.is_path_file_name(self.filename)
        self.fields = ["url", "Family_name", "Criminal_Name", "sex", "Date_of_birth", "Place_of_birth", "Language_spoken", "Nationality", "Charges", "Regions_where_wanted"]
        self.csv_file.writerow(self.fields)

    def is_path_file_name(self, excel_file_name):
        '''
        This function contains csv_file generation
        '''
        if os.path.isfile(excel_file_name):
            os.system('rm%s' % excel_file_name)
        oupf = open(excel_file_name, 'ab+')
        todays_excel_file = csv.writer(oupf)
        return todays_excel_file



    def parse(self, response):
        '''
        This function contains last pages_ navigations
        '''
        reference = response.url
        headers = {
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Origin': 'https://www.interpol.int',
            'Upgrade-Insecure-Requests': '1',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Referer': 'https://www.interpol.int/extension/design_sqli/design/design_sqli/stylesheets/master.css',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        }

        data = [('search', '1'), ('Name', self.keyword), ('Forename', ''), ('Nationality', ''), ('FreeText', ''), ('current_age_mini', '0'), ('current_age_maxi', '100'), ('Sex', ''), ('Eyes', ''), ('Hair', ''), ('RequestingCountry', ''), ('data', ''),]

        yield FormRequest('https://www.interpol.int/notice/search/wanted', callback=self.parse_next, headers=headers, formdata=data, meta={'reference':reference})


    def parse_next(self, response):
        '''
         This function contains required xpaths
        '''
        sel = Selector(response)
        reference = response.meta['reference']
        last_page_links = sel.xpath('//a[contains(@href, "/notice/search")]/@href').extract()
        for last_page in last_page_links:
            url = 'https://www.interpol.int' + last_page
            yield Request(url, self.parse_last_page_data, meta={'reference':reference})


    def parse_last_page_data(self, response):
        '''
        This function contains required xpaths
        '''
        sel = Selector(response)
        reference = response.url
        family_name = ''.join(sel.xpath('//tr//td[contains(text(), "Present family name:")]/following-sibling::td/text()').extract())
        fore_name = ''.join(sel.xpath('//tr//td[contains(text(), "Forename:")]/following-sibling::td/text()').extract())
        sex = ''.join(sel.xpath('//tr//td[contains(text(), "Sex:")]/following-sibling::td/text()').extract())
        date_of_birth = ''.join(sel.xpath('//tr//td[contains(text(), "Date of birth:")]/following-sibling::td/text()').extract())
        place_of_birth = ''.join(sel.xpath('//tr//td[contains(text(), "Place of birth:")]/following-sibling::td/text()').extract())
        language_spoken = ''.join(sel.xpath('//tr//td[contains(text(), "Language spoken:")]/following-sibling::td/text()').extract()).replace('\t', '').replace('\n', '')
        nationality = ''.join(sel.xpath('//tr//td[contains(text(), "Nationality:")]/following-sibling::td/text()').extract()).replace('\t', '').replace('\n', '')
        charges = ''.join(sel.xpath('//p[@class="charge"]//text()').extract()).replace(';', ',')
        regions_where_wanted = str(''.join(sel.xpath('//div//span[@class="nom_fugitif_wanted_small"]//text()').extract()))

        csv_values = [reference, family_name.encode('utf8'), fore_name.encode('utf8'), sex, date_of_birth, place_of_birth, language_spoken, nationality, charges.encode('utf8'), regions_where_wanted.encode('utf8')]
        self.csv_file.writerow(csv_values)

