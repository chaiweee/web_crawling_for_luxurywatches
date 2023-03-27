from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import urllib.request
import time
import random
from datetime import date
import json
from .functions import CrawlFunction, MySQLdb


def govberg_crawl():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome('/usr/bin/chromedriver', chrome_options=options)
    time.sleep(3)
    driver.get('https://www.govbergwatches.com/product-category/preowned-watches/')

    curUrl = driver.current_url
    time.sleep(random.uniform(2,4))

    # get all brand list
    select = driver.find_element_by_xpath('/html/body/div[2]/div[3]/div[7]/div/div[4]/div[1]/div[2]/aside[2]/h3')
    select.click()
    show_more = driver.find_element_by_xpath('/html/body/div[2]/div[3]/div[7]/div/div[4]/div[1]/div[2]/aside[2]/ul/li[9]')
    driver.execute_script("arguments[0].click();", show_more)

    time.sleep(5)

    brands = list(filter(CrawlFunction.isOverflow, driver.find_element_by_xpath('/html/body/div[2]/div[3]/div[7]/div/div[4]/div[1]/div[2]/aside[2]/ul').find_elements_by_tag_name('li')))
    brand_list = list(map(CrawlFunction.findValue, brands))

    # print('brands', brand_list, '================')

    time.sleep(5)

    while(1):
        liList = list(filter(CrawlFunction.isProduct, driver.find_element_by_xpath('//*[@id="shop_productarea"]/ul').find_elements_by_tag_name('li')))
        liList = list(map(CrawlFunction.findHref, liList))

        for child in liList:
            driver.get(child)
            # print(child)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            price = soup.find_all(class_ = 'woocommerce-Price-amount amount')
            title = soup.find_all(class_ = 'product_title entry-title')
            reference_number = soup.select('div.meta_row > div.meta_detail')
            images = soup.select('div.images > a.woocommerce-main-image')
        
            img = images[0].attrs['href']
            original_price = price[0].getText()
            sale_price = price[1].getText()
            oriPrice = CrawlFunction.emitDollar(original_price)
            salePrice = CrawlFunction.emitDollar(sale_price)

            ref_no = reference_number[0].getText().strip()
            model = title[0].getText()
            brand = ""

            for item in brand_list:
                if item in model:
                    brand = item
                    model = model.replace(item+' ', '').replace(ref_no, '')
            print('model ======>', model, 'brand =====>', brand)

            dbInst = MySQLdb()
            query = ''' SELECT * from tbl_crawl where brand=%s and model=%s and refNo=%s'''
            existed_watch = dbInst.fetchOne(query, (brand, model, ref_no))
            print('watch:',existed_watch)
            if existed_watch is None:
                query = ''' SELECT * from tbl_crawl where refNo=%s'''
                existed_refNo = dbInst.fetchOne(query, (ref_no))
                if existed_refNo is None:
                    print('add watch')
                    query2 = ''' INSERT INTO tbl_crawl(brand, model, refNo, original_price_govberg, price_govberg, reg_time, img) values (%s, %s, %s, %s, %s, %s, %s)'''
                    values2 = [brand, model, ref_no, oriPrice, salePrice, date.today(), img]
                else: 
                    query2 = ''' UPDATE tbl_crawl set price_govberg=%s, reg_time=%s where brand=%s and model=%s and refNo=%s'''
                    values2 = [salePrice, date.today(), brand, model, ref_no]
            else:
                print('update watch')
                if existed_watch['img'] is None:
                    print('no img')
                    query2 = ''' UPDATE tbl_crawl set price_govberg=%s, reg_time=%s, img=%s where brand=%s and model=%s and refNo=%s'''
                    values2 = [salePrice, date.today(), img, brand, model, ref_no]
                else:
                    print('img exist')
                    query2 = ''' UPDATE tbl_crawl set price_govberg=%s, reg_time=%s where brand=%s and model=%s and refNo=%s'''
                    values2 = [salePrice, date.today(), brand, model, ref_no]

            dbInst.execute(query2, values2)
            dbInst.disconnect()

            driver.back()
            time.sleep(3)

        driver.get(curUrl)
        time.sleep(random.uniform(2,4))

        next = list(filter(CrawlFunction.isNextBtn, driver.find_element_by_xpath('//*[@id="shop"]').find_elements_by_class_name('page-numbers')))
        if len(next) == 0:
            break

        next[0].click()
