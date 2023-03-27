from selenium import webdriver
from bs4 import BeautifulSoup
import time
from datetime import date
import json
import re
from .functions import CrawlFunction, MySQLdb
from currency_converter import CurrencyConverter

def watchq_crawl():
    domain = 'http://www.thewatchquote.com'

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome('/usr/bin/chromedriver', chrome_options=options)
    time.sleep(1)
    driver.get(domain + '/The-Luxury-Watches-Portal-No_5.htm')
    brandList = list(map(CrawlFunction.findHref, driver.find_element_by_id('tmpl_11038').find_elements_by_tag_name('td')))

    for url in brandList:
        driver.get(url)
        time.sleep(2)
        productUrls = driver.find_elements_by_tag_name('td')
        productUrls = list(filter(CrawlFunction.isPicto, productUrls))
        productUrls = list(map(CrawlFunction.findHref, productUrls))

        for productUrl in productUrls:
            if productUrl.startswith(domain):
                driver.get(productUrl)
            else:
                driver.get(domain + productUrl)

            try:
                targetSite1 = driver.current_url
                # print(targetSite1)
                body = driver.find_element_by_css_selector('body')
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                detail = soup.find_all(class_ = 'valeurs')
                detail_ = soup.select('tr.titre_neuf > td')
                price = soup.select('tr > td.valeur_neuf')
                src = soup.select('td > img')

                watch_img = src[1]
                img = watch_img.attrs['src']
                brand = detail_[0].getText()
                series = detail_[1].getText()
                model = detail_[2].getText()
                ref_no = detail[0].getText()
                sale_price = price[0].getText()
                sale_price = int(sale_price.replace('.00 €', '').replace(',', ''))
                c = CurrencyConverter()
                price_in_usd = c.convert(sale_price, 'GBP', 'USD')

                dbInst = MySQLdb()
                query = ''' SELECT * from tbl_crawl where brand=%s and model=%s and refNo=%s'''
                existed_watch = dbInst.fetchOne(query, (brand, model, ref_no))
                print(existed_watch)
                if existed_watch is None:
                    print('add watch')
                    query2 = ''' INSERT INTO tbl_crawl(brand, model, refNo, price_watchquote, reg_time, img) values (%s, %s, %s, %s, %s, %s)'''
                    values2 = [brand, model, ref_no, price_in_usd, date.today(), img]
                else:
                    print('update watch')
                    if existed_watch['img'] is None:
                        print('no img')
                        query2 = ''' UPDATE tbl_crawl set price_watchquote=%s, reg_time=%s, img=%s where brand=%s and model=%s and refNo=%s'''
                        values2 = [price_in_usd, date.today(), img, brand, model, ref_no]
                    else:
                        print('img exist')
                        query2 = ''' UPDATE tbl_crawl set price_watchquote=%s, reg_time=%s where brand=%s and model=%s and refNo=%s'''
                        values2 = [price_in_usd, date.today(), brand, model, ref_no]

                dbInst.execute(query2, values2)
                dbInst.disconnect()
            except:
                print('error : ' + targetSite1)

    # #list price 누른후 표에서 왼쪽에서부터 오른쪽으로 숫자 증가 ex)4번째줄에 첫번꺼 tr[4]/td[1]이런식으로
    # driver.find_element_by_xpath('//*[@id="tmpl_7844"]/div[8]/div[2]/table[2]/tbody/tr[2]/td[1]/table/tbody/tr/td/a/img').click()
    # #브랜드 들어와서 첫번째꺼 클릭하는것만새로이 해주기,그런다음에 div[]숫자만 바꾸면 됨
    # for i in range(1,15): #(몇개인지에따라서 마지막 끝숫자만바꾸면댐)
    #     driver.find_element_by_xpath('//*[@id="tmpl_8741"]/div[1]/div[8]/ul/li['+str(i)+']/a/img').click()
    # # driver.find_element_by_xpath('//*[@id="tmpl_8741"]/div[1]/div[8]/ul/li[2]/a/img').click()
    #     targetSite1 = driver.current_url
    #     print(targetSite1)
    #     body = driver.find_element_by_css_selector('body')
    #     soup = BeautifulSoup(driver.page_source, 'html.parser')
    #     detail = soup.find_all(class_ = 'valeurs')
    #     detail_ = soup.select('tr.titre_neuf > td')
    #     price = soup.select('tr > td.valeur_neuf')
    #     print('REFERENCE NUMBER = {}'.format(detail[0].getText()))
    #     print('RETAIL PRICE = {}'.format(price[0].getText()))
    #     print('BRAND = {}'.format(detail_[0].getText()))
    #     print('SERIES = {}'.format(detail_[1].getText()))
    #     print('MODEL = {}'.format(detail_[2].getText()))
    #     time.sleep(0.1)
