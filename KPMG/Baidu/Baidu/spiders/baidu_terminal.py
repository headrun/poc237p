from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re
import csv
import time
from datetime import datetime
import xlwt, csv
from hashlib import md5
import  MySQLdb
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from scrapy.selector import Selector
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import requests
from scrapy import log
from scrapy import signals
from scrapy.spider import Spider
from scrapy.http import FormRequest, Request
from scrapy.xlib.pydispatch import dispatcher
con = MySQLdb.connect(db   = 'BAIDU', \
    host = 'localhost', charset="utf8", use_unicode=True, \
    user = 'root', passwd ='root')
cur = con.cursor()
select_query = "select sk,url,main_keyword from baidu_crawl where crawl_status=0"
insert_query = "insert into baidu_metadata(url,name_of_url,description,created_at,modified_at) values(%s,%s,%s,now(),now()) on duplicate key update modified_at = now()"
update_query = 'update baidu_crawl set crawl_status=1 where crawl_status=0 and url="%s"'
class BaiduTerminal(Spider):
    name = "baidu_terminal"
    def __init__(self,*args, **kwargs):
	super(BaiduTerminal, self).__init__(*args, **kwargs)
        self.i=0
    def start_requests(self):
        cur.execute(select_query)
        data = cur.fetchall()
        for row in data :
            sk,url,main_keyword = row
            yield Request(url,callback=self.parse,meta={'keyword':main_keyword})
                                
    def parse(self,response):
        sel = Selector(response)
        keyword = response.meta['keyword'].replace('\n','').strip()
	node = sel.xpath('//h3')
        excel_file_name = 'baidu_%s_%s.csv' %(keyword ,str(datetime.date.today()))
        oupf = open(excel_file_name, 'ab+')
        todays_excel_file  = csv.writer(oupf)
        headers = ['name_of_url', 'url', 'description']
        todays_excel_file.writerow(headers)
        for nod in node:
                url = ''.join(nod.xpath('./a/@href').extract())
                sk = md5(url)
                name_of_url = ''.join(nod.xpath('.//a//text()').extract())
                description = ''.join(nod.xpath('.//following-sibling::div//text()').extract())
                if '.op_sp' in description:
                        description = ''.join(sel.xpath('//div[@class="op_sp_fanyi"]//text()').extract()).replace('\n','')
                if name_of_url and description:
                        values = (url,name_of_url,description)
                        cur.execute(insert_query,values)
                        con.commit()
                        todays_excel_file.writerow(values)
                        cur.execute(update_query % ''.join(url))
        page_navigation = ''.join(sel.xpath('//div[@id="page"]/a[normalize-space(text())]/text()').extract())
        page_navigation_link= ''.join(sel.xpath('//div[@id="page"]/a[contains(normalize-space(text()), ">")]/@href').extract())
        page_next = page_navigation_link
        if page_next:
            navigate_url = "http://www.baidu.com" + page_next
            yield Request(navigate_url,callback=self.parse,dont_filter=False,meta={'keyword':keyword})
