# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re
import datetime
import csv
import md5
import  MySQLdb
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from scrapy.selector import Selector



class BaiduBrowse(object):

    def __init__(self):
        self.con = MySQLdb.connect(db   = 'BAIDU', \
        host = 'localhost', charset="utf8", use_unicode=True, \
        user = 'root', passwd ='root')
        self.cur = self.con.cursor()
        self.insert_query = 'insert into baidu_crawl(sk, url, crawl_status, main_keyword, created_at, modified_at)values(%s,%s, %s, %s, now(), now()) on duplicate key update modified_at = now()'
        self.base_url = "http://www.baidu.com/"
        self.main()

    def get_driver(self):
        profile = webdriver.FirefoxProfile()
        driver = webdriver.Firefox(profile)
        time.sleep(4)
        driver.get(self.base_url + "/")
        driver.find_element_by_id("kw").clear()
        time.sleep(3)
        with open('keywords.txt', 'r') as f: rows = f.readlines()
        counter = 0
        for row in rows:
                time.sleep(5)
                counter += 1
                i = row.replace('\r\n','')
                driver.find_element_by_id("kw").clear()
                driver.wait = WebDriverWait(driver, 3)
                driver.find_element_by_id("kw").send_keys(i)
                time.sleep(3)
                ref_url = driver.current_url
                if counter > 1
                    driver.find_element_by_id("su").click()
                    time.sleep(3)
                    ref_url = driver.current_url
                sk = md5.md5(driver.current_url).hexdigest()
                vals = (sk,str(driver.current_url),'0',str(i))
                self.cur.execute(self.insert_query,vals)
                self.con.commit()



    def main(self):
        driver = self.get_driver()


if __name__ == "__main__":
    BaiduBrowse()

