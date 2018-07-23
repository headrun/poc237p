# -*- coding: utf-8 -*-
import csv
import datetime
from scrapy.http     import  Request
from scrapy.spider   import BaseSpider
from scrapy.selector import Selector
class EUROPEAN(BaseSpider):
    name = 'european_browse'
    start_urls = ['http://curia.europa.eu/juris/recherche.jsf?language=en']

    def __init__(self, prtynme='', **kwargs):
        super(EUROPEAN, self).__init__(**kwargs)
        self.prtynme = prtynme
        self.headers = ['Case Number', 'Title', 'Description', 'Date of Hearing',
                        'Date of Delivery', 'Advocate', 'Result']
        oupf1 = open('curia-%s-%s.csv'  % (self.prtynme, str(datetime.date.today())), 'wb+')
        self.csv_file = csv.writer(oupf1)
        self.csv_file.writerow(self.headers)
        self.headings = ['Case Number', 'Doc', 'Date', 'Parties', 'Subject-Matter']
        oupf2 = open('curia-%s-documents-%s.csv' %(self.prtynme, str(datetime.date.today())), 'wb+')
        self.document_file = csv.writer(oupf2)
        self.document_file.writerow(self.headings)

    def parse(self, response):
        dat1 = response.headers.getlist('Set-cookie')
        cook = {}
        for i in dat1:
            davn = i.split(';')[0]
            if davn:
                try:
                    key, val = davn.split('=', 1)
                except:
                    continue
                cook.update({key.strip():val.strip()})
        cookies = {'JSESSIONID': cook.get('JSESSIONID', '')}
        headers = {'Connection': 'keep-alive',
                   'Upgrade-Insecure-Requests': '1',
                   'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                   'Referer': 'http://curia.europa.eu/juris/recherche.jsf?language=en',
                   'Accept-Encoding': 'gzip, deflate',
                   'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',}
        yield Request('http://curia.europa.eu/juris/documents.jsf?pro=&nat=or&oqp=&dates=&lg=&language=en&jur=C%2CT%2CF&cit=none%252CC%252CCJ%252CR%252C2008E%252C%252C%252C%252C%252C%252C%252C%252C%252C%252Ctrue%252Cfalse%252Cfalse&td=%3BALL&pcs=Oor&avg=&page=1&mat=or&parties='+self.prtynme+'&jge=&for=&cid=137525', callback=self.parse_md2)
        yield Request('http://curia.europa.eu/juris/liste.jsf?pro=&nat=or&oqp=&dates=&lg=&language=en&jur=C%2CT%2CF&cit=none%252CC%252CCJ%252CR%252C2008E%252C%252C%252C%252C%252C%252C%252C%252C%252C%252Ctrue%252Cfalse%252Cfalse&td=%3BALL&pcs=Oor&avg=&page=1&mat=or&parties='+self.prtynme+'&jge=&for=&cid=137525', headers=headers, cookies=cookies, callback=self.parse_md)

    def parse_md(self, response):
        sel = Selector(response)
        nodes = sel.xpath("//div[@class='affaire']")
        for node in nodes:
            title = ''.join(node.xpath(".//span[@class='affaire_title']//text()").extract()).strip()
            case_no = '-'.join(title.split('-')[0:2])
            description = ''.join(node.xpath(".//div[@class='decision_title']//p//text()").extract()).encode('utf-8').strip()
            link = ''.join(node.xpath(".//span[@class='decision_links']//a//@href").extract())
            yield Request(link, callback=self.parse_md1, meta={'Case_no': case_no, 'description': description})

    def parse_md1(self, response):
        sel = Selector(response)
        delivery = ''.join(sel.xpath('//div[@class="detail_zone_content"]//h3[contains(text(), "delivery")]/following-sibling::p[1]//text()').extract()).strip()
        hearing = ''.join(sel.xpath('//div[@class="detail_zone_content"]//h3[contains(text(), "hearing")]/following-sibling::p[1]//text()').extract()).strip()
        parties = ''.join(sel.xpath('//div[@class="detail_zone_content"]//h3[contains(text(), "parties")]/following-sibling::p[1]//text()').extract()).encode('utf-8').strip()
        advocate = ''.join(sel.xpath('//div[@class="detail_zone_content"]//h3[contains(text(), "Advocate")]/following-sibling::p//text()').extract()).encode('utf-8').strip()
        result = ''.join(sel.xpath('//div[@class="detail_zone_content"]//h3[contains(text(), "result")]//following-sibling::ul[1]//li[contains(@id, "mainForm:j_id")]//text()').extract()).strip().encode('utf-8').strip()
        case = response.meta.get('Case_no', '')
        description = response.meta.get('description', '')
        values = [case, parties, description, hearing, delivery, advocate, result]
        self.csv_file.writerow(values)

    def parse_md2(self, response):
        sel = Selector(response)
        nodes = sel.xpath('//table[@class="detail_table_documents"]//tr[@class="table_document_ligne"]')
        for node in nodes:
            caseno = ''.join(node.xpath('.//td[@class="table_cell_aff"]//text()').extract()).strip()
            if 'OpenWin' in caseno:
                caseno = ''.join(node.xpath('.//td[@class="table_cell_aff"]//text()').extract()).strip().split('\n')[0]
            doc = ''.join(node.xpath('.//td[@class="table_cell_doc"]//text()').extract()).strip()
            date = ''.join(node.xpath('.//td[@class="table_cell_date"]//text()').extract()).strip()
            nparties = ''.join(node.xpath('.//td[@class="table_cell_nom_usuel"]//text()').extract()).strip()
            subjectmatter = ''.join(node.xpath('.//td[@class="table_cell_links_curia"]//text()').extract()).strip()
            values = [caseno, doc, date, nparties, subjectmatter]
            self.document_file.writerow(values)
        nxt_pg = response.xpath('//a[img[contains(@title, "next document")]]/@href').extract()
        nxt = ''.join(nxt_pg)
        if nxt:
            yield Request(nxt, callback=self.parse_md2)
