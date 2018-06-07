import re
import time
import json
import urllib
import requests
import csv
import sys
import datetime
reload(sys)
sys.setdefaultencoding("utf-8")

from scrapy.http     import  Request, FormRequest
from scrapy.spider   import BaseSpider
from scrapy.selector import Selector
  
class CIBIL(BaseSpider):
    name = 'CIBIL_browse'
    #start_urls = ['https://suit.cibil.com/']

    def __init__(self, borrower = '', amount = '', **kwargs):
        super(CIBIL, self).__init__(**kwargs)
        self.amount = amount
        self.borrower = borrower
	self.headers = ['PageNo', 'BankName','BankID','BranchName','BranchID','BranchCode','QuarterID','QuarterDate','QuarterDateStr','QuarterName','QuarterMonthStr','QuarterYearStr','BorrowerName','DirectorName','Reg_Address','OutstandingAmount'] 
        oupf1 = open('CIBIL-%s-%s.csv'  % (self.borrower, str(datetime.date.today())), 'wb+')
        self.csv_file  = csv.writer(oupf1) 
        self.csv_file.writerow(self.headers)
  
    def start_requests(self):

	headers = {
	    'Connection': 'keep-alive',
	    'Upgrade-Insecure-Requests': '1',
	    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
	    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
	    'Accept-Encoding': 'gzip, deflate, br',  
	    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
	}

	yield Request('https://suit.cibil.com/', headers=headers, callback = self.parse)

    '''def parse(self, response):
        dat = response.headers.getlist('Set-cookie')
        cook = {}
        for i in dat:
            da = i.split(';')[0]
            if da:
                try: key, val = da.split('=', 1)
                except : continue
                cook.update({key.strip():val.strip()})
        headers = {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Origin': 'https://suit.cibil.com',
            'Upgrade-Insecure-Requests': '1',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Macintiiiiiosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Referer': 'https://suit.cibil.com/',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        }

        cookies = {
            'JSESSIONID':cook.get('JSESSIONID',''),
            'NSC_WJQ_tvju.djcjm.dpn_100.205':cook.get('NSC_WJQ_tvju.djcjm.dpn_100.205','')
        }
        data = [
          ('quarterIdSummary', '0'),
          ('quarterIdGrantors', '0'),
          ('croreAccount', '1'),
          ('quarterIdCrore', '0'),
          ('lakhAccount', '1'),
          ('quarterIdLakh', '0'),
          ('quarterDateStr', 'ALL'),
          ('fileType', '2'),
          ('searchMode', '1'),
        ]

        yield FormRequest('https://suit.cibil.com/loadSuitFiledDataSearchAction', headers=headers, cookies=cook, formdata=data, method="POST", callback= self.parse_new, meta= {'cook_new':cook})'''
 
    def parse(self, response):  
	new_cook = response.meta.get('cook_new','')
 	dat1 = response.headers.getlist('Set-cookie')
        cook = {}
        for i in dat1:
            da = i.split(';')[0]
            if da:
                try: key, val = da.split('=', 1)
                except : continue
                cook.update({key.strip():val.strip()})
	headers = {
	    'Accept-Encoding': 'gzip, deflate, br',
	    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
	    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
	    'Accept': 'application/json, text/javascript, */*; q=0.01',
	    'Referer': 'https://suit.cibil.com/suitFiledAccountSearchAction',
	    'X-Requested-With': 'XMLHttpRequest',
	    'Connection': 'keep-alive',
	}
	
	cookies = {
            'JSESSIONID':cook.get('JSESSIONID',''),
            'NSC_WJQ_tvju.djcjm.dpn_100.205':cook.get('NSC_WJQ_tvju.djcjm.dpn_100.205','')
        }

        meta = {u'bankBean': {u'categoryBean': {u'active': 0, u'enable': False, u'categoryAllotedId': u'', u'categoryId': 0, u'categoryName': u''}, u'enable': False, u'bankName': u'', u'bankId': 0, u'active': 0, u'bankNoRecords': 0, u'bankTotalAmount': u''}, u'firstLimit': 0, u'borrowerName': self.borrower, u'stateName': u'', u'userId': 0, u'uploadBatchBean': None, u'stateBean': {u'category': u'', u'stateNoRecords': 0, u'enable': False, u'stateId': 0, u'stateName': u'', u'stateTotalAmount': u'', u'isActive': 0}, u'noOFCGs25Lac': 0, u'editedDirectorPan': None, u'quarterId': 0, u'dinNumber': u'', u'city': u'', u'categoryBean': None, u'isReview': u'', u'title': u'', u'editedDirectorNames': None, u'userComments': u'', u'branchBean': None, u'dunsNumber': u'', u'totalRecords': 0, u'rejectComment': u'', u'catGroup': u'', u'records1Cr': 0, u'reject': None, u'lastLimit': 0, u'totalAmount': u'', u'summaryType': u'', u'noOFCGs1Cr': 0, u'sortOrder': None, u'sort': 0, u'directorSuffix': u'', u'summaryState': u'', u'editedDirectorDin': None, u'srNo': u'', u'rejectComments': None, u'editedTotalAmount': None, u'modify': None, u'updateReject': u'', u'rejected': 0, u'quarterBean': {u'quarterDateStr': u'', u'quarterYearStr': u'', u'quarterMonthStr': u'', u'isPush': 0, u'quarterName': u'', u'quarterId': 0, u'quarterDate': None}, u'directorBean': {u'dinDir': u'', u'panDir': u'', u'dirp25lId': 0, u'dirPrefix': None, u'dirp1crId': 0, u'dirStatus': None, u'dirSufix': None, u'dirId': 0, u'dirDeleteDate': None, u'dir': None}, u'dirPan': u'', u'sortBy': None, u'borrowerId': 0, u'borrowerAddress': None, u'fromQuarterId': 0, u'toQuarterId': 0, u'importDataBean': None, u'edit': None, u'costAmount': u'', u'directorId': 0, u'cat': u'', u'partyTypeId': 0, u'directorName': u'', u'records25Lac': 0, u'quarterCol': u'', u'user': None}
        if self.amount in ['100', 100]:
        #if self.amount == '100' :
            params = (
                ('fileType', '2'),
                ('suitSearchBeanJson', json.dumps(meta)),
                ('_search', 'false'),
                ('nd', str(int(time.time()*1000))),
                ('rows', '15'),
                ('page', '1'),
                ('sidx', ''),
                ('sord', 'asc'),
            )

        else:
            params = (
                ('fileType', '1'),
                ('suitSearchBeanJson', json.dumps(meta)),
                ('_search', 'false'),
                ('nd', str(int(time.time()*1000))),
                ('rows', '15'),
                ('page', '1'),
                ('sidx', ''),
                ('sord', 'asc'),
            ) 
       
	url_params = urllib.urlencode(params)
        url = "https://suit.cibil.com/loadSearchResultPage?" + url_params
        yield FormRequest(url,  headers=headers,cookies=cookies, callback = self.parse_final, meta={'meta':meta, 'cook': cook})

    def parse_final(self, response):
	meta = response.meta.get('meta','')
	cook_now = response.meta.get('cook','')
	data = json.loads(response.body)
        page_num = data.get('page','')
	rows = data.get('rows','')
        for row in rows:
            bankname = row.get('branchBean',{}).get('bankBean',{}).get('bankName','')
            bankid = row.get('branchBean',{}).get('bankBean',{}).get('bankId','')
            branchname = row.get('branchBean',{}).get('branchName','')
            branchid = row.get('branchBean',{}).get('branchId','')
            branchcode = row.get('branchBean',{}).get('branchcode','')
            quarterId = row.get('quarterBean',{}).get('quarterId','')
            quarterDate = row.get('quarterBean',{}).get('quarterDate','')
            quarterDateStr = row.get('quarterBean',{}).get('quarterDateStr','')
            quarterName = row.get('quarterBean',{}).get('quarterName','')
            quarterMonthStr = row.get('quarterBean',{}).get('quarterMonthStr','')
            quarterYearStr = row.get('quarterBean',{}).get('quarterYearStr','')
            borrowerName = row.get('borrowerName','')
            directorName = row.get('directorName','')
            regaddress = row.get('importDataBean',{}).get('regaddr','')
            outstanding_amt = row.get('branchBean',{}).get('bankBean',{}).get('bankTotalAmount',{})

	    values = [page_num, bankname,bankid,branchname,branchid,branchcode,quarterId,quarterDate,quarterDateStr,quarterName,quarterMonthStr,quarterYearStr,borrowerName,directorName,regaddress,outstanding_amt]
            self.csv_file.writerow(values)

	total_pages = data.get('total','1')   
	total_records = data.get('records','0')
	page_num =  data.get('page','0') 
	if(int(total_pages)>1): 
	    #if int(total_pages) == int(page_num): 
		#break
	    for each_page in range(2, total_pages+1): 
		lat_cook = response.meta.get('cook','')
		my_dict = response.request.headers.getlist('Cookie')
		cook = {}
		for i in my_dict:
		    da = i.split(';')
		    if da:
			try: key, val = da
			except : continue 
			cook.update({key.strip():val.strip()})
		headers = {
		'Accept-Encoding': 'gzip, deflate, br',
		'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
		'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
		'Accept': 'application/json, text/javascript, */*; q=0.01',
		'Referer': 'https://suit.cibil.com/suitFiledAccountSearchAction',
		'X-Requested-With': 'XMLHttpRequest',
		'Connection': 'keep-alive',
		}
		
		cookies = {
		'JSESSIONID':cook_now.get('JSESSIONID',''),
		'NSC_WJQ_tvju.djcjm.dpn_100.205':cook_now.get('NSC_WJQ_tvju.djcjm.dpn_100.205','')
		}
		
		if self.amount in ['100', 100]:  

		    params = (
			('fileType', '2'),
			('suitSearchBeanJson', json.dumps(meta)),
			('_search', 'false'),
			('nd', str(int(time.time()*1000))),
			('rows', '15'),
			('page', str(each_page)),
			('sidx', ''),
			('sord', 'asc'),
			)
		else:
		    params = (
			('fileType', '1'),
			('suitSearchBeanJson', json.dumps(meta)),
			('_search', 'false'),
			('nd', str(int(time.time()*1000))),
			('rows', '15'),
			('page', str(each_page)),
			('sidx', ''),
			('sord', 'asc'),
			)
		url_params = urllib.urlencode(params)
		next_url = "https://suit.cibil.com/loadSearchResultPage?" + url_params 
		yield Request(next_url, headers=headers, cookies=cookies,  callback = self.parse_last)


    def parse_last(self,response):
	data = json.loads(response.body)
        page_num = data.get('page','')
        rows = data.get('rows','')
        print page_num, '>>>>>>>>>>>>>'
        for row in rows:
            bankname = row.get('branchBean',{}).get('bankBean',{}).get('bankName','')
            bankid = row.get('branchBean',{}).get('bankBean',{}).get('bankId','')
            branchname = row.get('branchBean',{}).get('branchName','')
            branchid = row.get('branchBean',{}).get('branchId','')
            branchcode = row.get('branchBean',{}).get('branchcode','')
            quarterId = row.get('quarterBean',{}).get('quarterId','')
            quarterDate = row.get('quarterBean',{}).get('quarterDate','')
            quarterDateStr = row.get('quarterBean',{}).get('quarterDateStr','')
            quarterName = row.get('quarterBean',{}).get('quarterName','')
            quarterMonthStr = row.get('quarterBean',{}).get('quarterMonthStr','')
            quarterYearStr = row.get('quarterBean',{}).get('quarterYearStr','')
            borrowerName = row.get('borrowerName','')
            directorName = row.get('directorName','')
            regaddress = row.get('importDataBean',{}).get('regaddr','')
            outstanding_amt = row.get('bankBean',{}).get('bankTotalAmount',{})
      
            
            values = [page_num, bankname,bankid,branchname,branchid,branchcode,quarterId,quarterDate,quarterDateStr,quarterName,quarterMonthStr,quarterYearStr,borrowerName,directorName,regaddress,outstanding_amt]
	    self.csv_file.writerow(values)
    
