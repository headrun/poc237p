import scrapy
from scrapy.http import FormRequest, Request
from scrapy.selector import Selector
import re
import json
import csv
import datetime
import sys

reload(sys)
sys.setdefaultencoding('utf8')


class Linkedin_companies(scrapy.Spider):
    name = 'linkedin_posts'
    allowed_domains = ["linkedin.com"]
    start_urls = ('https://www.linkedin.com/uas/login?goback=&trk=hb_signin',)

    def __init__(self, *args, **kwargs):
        self.excel_file_name = 'linkedinposts1_data_%s.csv' % str(
            datetime.datetime.now().date())
        oupf = open(self.excel_file_name, 'ab+')
        self.todays_excel_file = csv.writer(oupf)
        self.header_params = ['First Name', 'Last Name', 'Occupation', 'Information', 'Likes', 'Crawler']
        self.todays_excel_file.writerow(self.header_params)

    def parse(self, response):
	sel = Selector(response)
	logincsrf = ''.join(sel.xpath('//input[@name="loginCsrfParam"]/@value').extract())
	csrf_token = ''.join(sel.xpath('//input[@id="csrfToken-login"]/@value').extract())
	source_alias = ''.join(sel.xpath('//input[@name="sourceAlias"]/@value').extract())
	data = [
	  ('isJsEnabled', 'true'),
	  ('source_app', ''),
	  ('tryCount', ''),
	  ('clickedSuggestion', 'false'),
	  ('session_key', 'ramyalatha3004@gmail.com'),
	  ('session_password', '01491a0237'),
	  ('signin', 'Sign In'),
	  ('session_redirect', ''),
	  ('trk', 'hb_signin'),
	  ('loginCsrfParam', logincsrf),
	  ('fromEmail', ''),
	  ('csrfToken', csrf_token),
	  ('sourceAlias', source_alias),
	  ('client_v', '1.0.1'),
	]
	headers = {
	    'cookie': response.headers.getlist('Set-Cookie'),
	    'origin': 'https://www.linkedin.com',
	    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
	    'x-requested-with': 'XMLHttpRequest',
	    'x-isajaxform': '1',
	    'accept-encoding': 'gzip, deflate, br',
	    'pragma': 'no-cache',
	    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36',
	    'content-type': 'application/x-www-form-urlencoded',
	    'accept': '*/*',
	    'cache-control': 'no-cache',
	    'authority': 'www.linkedin.com',
	    'referer': 'https://www.linkedin.com/',
	}
	yield FormRequest('https://www.linkedin.com/uas/login-submit', callback=self.parse_next, formdata=data, headers = headers, meta = {"csrf_token":csrf_token})



    def parse_next(self, response):
        cooki_list = response.request.headers.get('Cookie', [])
	
        li_at_cookie = ''.join(re.findall('li_at=(.*?); ', cooki_list))
        headers = {
            'cookie': 'li_at=%s;JSESSIONID="%s"' % (li_at_cookie, response.meta['csrf_token']),
                'x-restli-protocol-version': '2.0.0',
                'x-requested-with': 'XMLHttpRequest',
                'csrf-token': response.meta['csrf_token'],
                'authority': 'www.linkedin.com',
                'referer': 'https://www.linkedin.com/search/results/index/?keywords=kpmg&origin=GLOBAL_SEARCH_HEADER',
        }
	api_url = "https://www.linkedin.com/voyager/api/search/cluster?count=6&guides=List(v-%3ECONTENT)&keywords=kpmg&origin=SWITCH_SEARCH_VERTICAL&q=guided&start=0"
        yield Request(api_url, callback=self.parse_again, headers=headers, meta={"main_url":"https://www.linkedin.com/voyager/api/search/hits?guides=List(v->CONTENT)&keywords=kpmg&origin=SWITCH_SEARCH_VERTICAL&q=guided", "headers":headers, "nav":"false"})

    def parse_again(self, response):
        json_tmp = json.loads(response.body)
        json_elements = json_tmp.get('elements',[])
	url_paging  = json_tmp.get('paging',[])
	headers = response.meta.get('headers', '')
	main_url = response.meta.get('main_url')
	if response.meta.get('nav') == "false":
		for element in json_elements:
		    each_element = element.get('elements')
		    for element in each_element:
			profile =  element.get('hitInfo', {}).get('com.linkedin.voyager.feed.Update',{}).get('value',{}).get('com.linkedin.voyager.feed.ShareUpdate',{}).get('actor',{}).get('com.linkedin.voyager.feed.MemberActor',{}).get('miniProfile',{})
			if profile:
				first_name = profile.get('firstName','')
				last_name = profile.get('lastName','')
				occupation = profile.get('occupation','')
				content = element.get('hitInfo', {}).get('com.linkedin.voyager.feed.Update',{}).get('value',{}).get('com.linkedin.voyager.feed.ShareUpdate',{}).get('content',{}).get('com.linkedin.voyager.feed.ShareText',{}).get('text',{}).get('values',[])
				likes = element.get('hitInfo',{}).get('com.linkedin.voyager.feed.Update',{}).get('socialDetail',{}).get('totalSocialActivityCounts',{}).get('numLikes','')
                                comments = element.get('hitInfo', {}).get('com.linkedin.voyager.feed.Update',{}).get('socialDetail',{}).get('totalSocialActivityCounts',{}).get('numComments','')
				for info in content:
				    information = info.get('value','')
				    values = [first_name, last_name, occupation, information, likes, comments]
				    print values
				    self.todays_excel_file.writerow(values)
			else:
				profile = element.get('hitInfo',{}).get('com.linkedin.voyager.feed.Update',{}).get('value',{}).get('com.linkedin.voyager.feed.ArticleUpdate',{}).get('content',{}).get('com.linkedin.voyager.feed.ShareArticle',{}).get('article',{}).get('article',{}).get('title','')
                                likes = element.get('hitInfo',{}).get('com.linkedin.voyager.feed.Update',{}).get('socialDetail',{}).get('totalSocialActivityCounts',{}).get('numLikes','')
                                comments = element.get('hitInfo', {}).get('com.linkedin.voyager.feed.Update',{}).get('socialDetail',{}).get('totalSocialActivityCounts',{}).get('numComments','')
                                values = [profile,'','','',likes,comments]
                                self.todays_excel_file.writerow(values)
	else:
		for eachjso in json_elements:
		       	id = eachjso.get('hitInfo', {}).get('com.linkedin.voyager.feed.Update', {}).get('id', '')
			profile = eachjso.get('hitInfo', {}).get('com.linkedin.voyager.feed.Update',{}).get('value',{}).get('com.linkedin.voyager.feed.ShareUpdate',{}).get('actor',{}).get('com.linkedin.voyager.feed.MemberActor',{}).get('miniProfile',{})
			if profile:
				first_name = profile.get('firstName','')
				last_name = profile.get('lastName','')
				occupation = profile.get('occupation','')
				content = eachjso.get('hitInfo', {}).get('com.linkedin.voyager.feed.Update',{}).get('value',{}).get('com.linkedin.voyager.feed.ShareUpdate',{}).get('content',{}).get('com.linkedin.voyager.feed.ShareText',{}).get('text',{}).get('values','')
				for info in content:
					information = info.get('value','')
					likes = eachjso.get('hitInfo',{}).get('com.linkedin.voyager.feed.Update',{}).get('socialDetail',{}).get('totalSocialActivityCounts',{}).get('numLikes','')
					comments = eachjso.get('hitInfo', {}).get('com.linkedin.voyager.feed.Update',{}).get('socialDetail',{}).get('totalSocialActivityCounts',{}).get('numComments','')
					values = [first_name,last_name,occupation,information,likes,comments]
					self.todays_excel_file.writerow(values)
			else:
				profile = eachjso.get('hitInfo',{}).get('com.linkedin.voyager.feed.Update',{}).get('value',{}).get('com.linkedin.voyager.feed.ArticleUpdate',{}).get('content',{}).get('com.linkedin.voyager.feed.ShareArticle',{}).get('article',{}).get('article',{}).get('title','')
				likes = eachjso.get('hitInfo',{}).get('com.linkedin.voyager.feed.Update',{}).get('socialDetail',{}).get('totalSocialActivityCounts',{}).get('numLikes','')
				comments = eachjso.get('hitInfo', {}).get('com.linkedin.voyager.feed.Update',{}).get('socialDetail',{}).get('totalSocialActivityCounts',{}).get('numComments','')
				values = [profile,'','','',likes,comments]
				self.todays_excel_file.writerow(values)

	if url_paging:
		count_data = url_paging.get('count','')
		start_data = url_paging.get('start','')
		total_data = url_paging.get('total','')
		if total_data > count_data+start_data and json_elements:
			cons_part = "&count=%s&start=%s"%(count_data, start_data+count_data)
			retrun_url = "%s%s"%(main_url,cons_part)
			yield Request(retrun_url, headers=headers, callback=self.parse_again, meta={'main_url':main_url, 'headers':headers, "nav":"true"})
