# Importing setup from celery service
import setup
from courts.models import CourtsRajasthancourt

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

class RajasthanHCSpider(BaseSpider):
    name = 'rajashighcourt_browse'
    start_urls = ['http://rhccasestatus.raj.nic.in/rhcpcis/']

    def __init__(self, partyname = '', year='', **kwargs):
        arguments = kwargs.get('myargs', {})
        arguments = json.loads(arguments)
        self.partyname = arguments.get('keyword', '')
        self.brand_id = kwargs.get('brand_id', 0)

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
        yield FormRequest('http://rhccasestatus.raj.nic.in/rhcpcis/kquarylobisparty.asp?id=get', headers=headers, cookies=cookies, formdata=data, method="POST", meta = {'allow_redirects':False, 'cook':cookies}, callback = self.parse_data)

    def parse_data(self, response):
        sel = Selector(response)
        nodes = sel.xpath('//table[@border="1"]//tr')
        for node in nodes:
            srno = ''.join(node.xpath('.//td[1]//text()').extract()).strip()
            case = ''.join(node.xpath('.//td[2]//text()').extract()).strip()
            url = ''.join(node.xpath('.//td[2]//a/@href').extract()).strip()
            case_url = "http://rhccasestatus.raj.nic.in/rhcpcis/" + url
            party_details = ''.join(node.xpath('.//td[3]//text()').extract()).strip()
            advocate_details = ''.join(node.xpath('.//td[4]//text()').extract()).strip()
            data = {
                    'case':case,
                    'case_url':case_url,
                    }
            if url.strip():yield Request(case_url, callback = self.parse_caseinfo, meta={'data':data})
        next_url = ''.join(sel.xpath('//a[contains(text(), "Next")]/@href').extract())
        print next_url
        complete_url = 'http://rhccasestatus.raj.nic.in/rhcpcis/'+ next_url.strip('/')

        cookies = response.meta.get('cook', {})

        headers = {
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Referer': 'http://rhccasestatus.raj.nic.in/rhcpcis/kquarylobisparty1.asp',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'en-US,en;q=0.9',
                }
        yield Request(complete_url, callback=self.parse_data, headers=headers, cookies=cookies)



    def parse_caseinfo(self, response):
        sel = Selector(response)
        data = response.meta.get('data', {})
        petitioner =  ''.join(sel.xpath('//*[@id="FrmMain"]/table[1]/tr[3]/td[3]/font//text()').extract()).strip()
        respondent = ''.join(sel.xpath('//*[@id="FrmMain"]/table[1]/tr[4]/td[3]/font//text()').extract()).strip()
        petitioner_advocate = ''.join(sel.xpath('//*[@id="FrmMain"]/table[1]/tr[5]/td[3]/font//text()').extract()).strip()
        rep_advocate = ''.join(sel.xpath('//*[@id="FrmMain"]/table[1]/tr[6]/td[3]/font//text()').extract()).strip()
        class_code = ''.join(sel.xpath('//*[@id="FrmMain"]/table[1]/tr[7]/td[3]/font//text()').extract()).strip()
        bench = ''.join(sel.xpath('//*[@id="FrmMain"]/table[1]/tr[8]/td[3]/font//text()').extract()).strip()
        listing_date = ''.join(sel.xpath('//*[@id="FrmMain"]/table[1]/tr[11]/td[3]/font//text()').extract()).strip()
        filing_no = ''.join(sel.xpath('//*[@id="FrmMain"]/table[2]/tr[3]/td[1]/font//text()').extract()).strip()
        filing_date = ''.join(sel.xpath('//*[@id="FrmMain"]/table[2]/tr[3]/td[3]/font//text()').extract()).strip()
        case_status = ''.join(sel.xpath('//form[@id="FrmMain"]//p[@align="center"]/font/text()').extract()).strip()
        #import pdb;pdb.set_trace()
        #values = [srno, case, case_url, party_details, advocate_details]
        values  = [data.get('case',''),data.get('case_url', ''), petitioner, respondent,  petitioner_advocate, rep_advocate, class_code, bench, listing_date, filing_no, filing_date, case_status]
        p, created = CourtsRajasthancourt.objects.get_or_create(case_no=data.get('case','').strip(), case_url=data.get('case_url', '').strip(), petitioner=petitioner, respondent=respondent, petitioner_advocate=petitioner_advocate, rep_advocate=rep_advocate, class_code=class_code, bench=bench, listing_date=listing_date, filing_no=filing_no, filing_date=filing_date, case_status=case_status, brand_id=self.brand_id)
        if not created:setattr(p, 'case_status', case_status)
        p.save()
        print values
#self.csv_file.writerow(values)
