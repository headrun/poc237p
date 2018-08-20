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
    name = 'linkedin_jobs_browse'
    allowed_domains = ["linkedin.com"]
    start_urls = ('https://www.linkedin.com/uas/login?goback=&trk=hb_signin',)

    def __init__(self, *args, **kwargs):
        self.excel_file_name = 'linkedin_jobs_data_%s.csv' % str(
            datetime.datetime.now().date())
        oupf = open(self.excel_file_name, 'ab+')
        self.todays_excel_file = csv.writer(oupf)
        self.header_params = ['company_id', 'jobview_url', 'Position(Company)']
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
	api_url = "https://www.linkedin.com/voyager/api/search/hits?decoration=%28hitInfo%28com.linkedin.voyager.search.SearchJobJserp%28descriptionSnippet%2CjobPosting~%28entityUrn%2CsavingInfo%2Ctitle%2CformattedLocation%2CapplyingInfo%2Cnew%2CjobState%2CsourceDomain%2CapplyMethod%28com.linkedin.voyager.jobs.OffsiteApply%2Ccom.linkedin.voyager.jobs.SimpleOnsiteApply%2Ccom.linkedin.voyager.jobs.ComplexOnsiteApply%29%2ClistedAt%2CexpireAt%2CclosedAt%2CcompanyDetails%28com.linkedin.voyager.jobs.JobPostingCompany%28company~%28entityUrn%2Cname%2Clogo%2CbackgroundCoverImage%29%29%2Ccom.linkedin.voyager.jobs.JobPostingCompanyName%29%2ClistingType%2CurlPathSegment%2CmatchType%2CmessagingToken%2CmessagingStatus%2CyearsOfExperienceMatch%2CdegreeMatches*%2CskillMatches*%2CstandardizedAddresses%2C~relevanceReason%28entityUrn%2CjobPosting%2Cdetails%28com.linkedin.voyager.jobs.shared.InNetworkRelevanceReasonDetails%28totalNumberOfConnections%2CtopConnections*~%28profilePicture%2CfirstName%2ClastName%2CentityUrn%29%29%2Ccom.linkedin.voyager.jobs.shared.CompanyRecruitRelevanceReasonDetails%28totalNumberOfPastCoworkers%2CcurrentCompany~%28entityUrn%2Cname%2Clogo%2CbackgroundCoverImage%29%29%2Ccom.linkedin.voyager.jobs.shared.SchoolRecruitRelevanceReasonDetails%28totalNumberOfAlumni%2CmostRecentSchool~%28entityUrn%2Cname%2Clogo%29%29%2Ccom.linkedin.voyager.jobs.shared.HiddenGemRelevanceReasonDetails%2Ccom.linkedin.voyager.jobs.shared.JobSeekerQualifiedRelevanceReasonDetails%29%29%2C~preferredCommuteRelevanceReason%28entityUrn%2CjobPosting%2CjobPostingRelevanceReasonDetail%28relevanceReasonFlavor%2CtravelMode%2CmaximumCommuteTravelTimeMinutes%29%29%29%2Csponsored%2CencryptedBiddingParameters%29%2Ccom.linkedin.voyager.*%29%2CtrackingId%29&count=25&f_C=List()&f_CF=List()&f_E=List()&f_ES=List()&f_ET=List()&f_F=List()&f_GC=List()&f_I=List()&f_JT=List()&f_L=List()&f_LF=List()&f_SB=List()&f_SB2=List()&f_SB3=List()&f_T=List()&f_TP=List()&keywords=kpmg&origin=JOB_SEARCH_RESULTS_PAGE&q=jserpAll&query=search&sortBy=R"
        yield Request(api_url, callback=self.parse_again, headers=headers, meta = {'headers':headers, 'main_url':"https://www.linkedin.com/voyager/api/search/hits?decoration=%28hitInfo%28com.linkedin.voyager.search.SearchJobJserp%28descriptionSnippet%2CjobPosting~%28entityUrn%2CsavingInfo%2Ctitle%2CformattedLocation%2CapplyingInfo%2Cnew%2CjobState%2CsourceDomain%2CapplyMethod%28com.linkedin.voyager.jobs.OffsiteApply%2Ccom.linkedin.voyager.jobs.SimpleOnsiteApply%2Ccom.linkedin.voyager.jobs.ComplexOnsiteApply%29%2ClistedAt%2CexpireAt%2CclosedAt%2CcompanyDetails%28com.linkedin.voyager.jobs.JobPostingCompany%28company~%28entityUrn%2Cname%2Clogo%2CbackgroundCoverImage%29%29%2Ccom.linkedin.voyager.jobs.JobPostingCompanyName%29%2ClistingType%2CurlPathSegment%2CmatchType%2CmessagingToken%2CmessagingStatus%2CyearsOfExperienceMatch%2CdegreeMatches*%2CskillMatches*%2CstandardizedAddresses%2C~relevanceReason%28entityUrn%2CjobPosting%2Cdetails%28com.linkedin.voyager.jobs.shared.InNetworkRelevanceReasonDetails%28totalNumberOfConnections%2CtopConnections*~%28profilePicture%2CfirstName%2ClastName%2CentityUrn%29%29%2Ccom.linkedin.voyager.jobs.shared.CompanyRecruitRelevanceReasonDetails%28totalNumberOfPastCoworkers%2CcurrentCompany~%28entityUrn%2Cname%2Clogo%2CbackgroundCoverImage%29%29%2Ccom.linkedin.voyager.jobs.shared.SchoolRecruitRelevanceReasonDetails%28totalNumberOfAlumni%2CmostRecentSchool~%28entityUrn%2Cname%2Clogo%29%29%2Ccom.linkedin.voyager.jobs.shared.HiddenGemRelevanceReasonDetails%2Ccom.linkedin.voyager.jobs.shared.JobSeekerQualifiedRelevanceReasonDetails%29%29%2C~preferredCommuteRelevanceReason%28entityUrn%2CjobPosting%2CjobPostingRelevanceReasonDetail%28relevanceReasonFlavor%2CtravelMode%2CmaximumCommuteTravelTimeMinutes%29%29%29%2Csponsored%2CencryptedBiddingParameters%29%2Ccom.linkedin.voyager.*%29%2CtrackingId%29&f_C=List()&f_CF=List()&f_E=List()&f_ES=List()&f_ET=List()&f_F=List()&f_GC=List()&f_I=List()&f_JT=List()&f_L=List()&f_LF=List()&f_SB=List()&f_SB2=List()&f_SB3=List()&f_T=List()&f_TP=List()&keywords=kpmg&origin=JOB_SEARCH_RESULTS_PAGE&q=jserpAll&query=search&sortBy=R"})

    def parse_again(self, response):
	main_url = response.meta.get('main_url','')
	json_tmp = json.loads(response.body)
	inner_elements = json_tmp.get('elements', [])
	headers = response.meta.get('headers','')
	for element in inner_elements:
	    compnay_id = ''.join(element.get('hitInfo', {}).get(
		'com.linkedin.voyager.search.SearchJobJserp', {}).get('jobPosting', ''))
	    compnay_full_id = compnay_id.split('jobPosting:')[-1]
	    job_view_url = ''.join(
		"https://www.linkedin.com/jobs/view/%s/" % (compnay_full_id))
	    company_title = ''.join(element.get('hitInfo', {}).get(
		'com.linkedin.voyager.search.SearchJobJserp', {}).get('jobPostingResolutionResult', {}).get('title', ''))
	    values = [compnay_full_id, job_view_url, company_title]
	    self.todays_excel_file.writerow(values)
	url_paging  = json_tmp.get('paging',[])
	if url_paging:
		count_data = url_paging.get('count','')
		start_data = url_paging.get('start','')
		total_data = url_paging.get('total','')
		#if total_data > count_data+start_data:
		if total_data > count_data+start_data and inner_elements:
			cons_part = "&count=%s&start=%s"%(count_data, start_data+count_data)
			retrun_url = "%s%s"%(main_url,cons_part)
			yield Request(retrun_url, headers=headers, callback=self.parse_again, meta={'main_url':main_url, 'headers':headers, "nav":"true"})
