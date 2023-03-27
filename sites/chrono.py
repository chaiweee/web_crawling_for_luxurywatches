from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import time
import json
from .functions import MySQLdb
from datetime import date

def chrono_crawl():
    base_url = "https://www.chrono24.com/"
    webpage = requests.get(base_url+'search/browse.htm?char=A-Z')
    soup = BeautifulSoup(webpage.content, "html.parser")
    dataArray = []

    a_tags = soup.find_all("a", {'class':"text-default"})

    count = 1
    urlArray = []
    for a_tag in a_tags :
        urlArray.append(str(a_tag["href"]))
        count += 1
    del urlArray[0]

    for i in range(0, len(urlArray)):
        counter = 1
        while 1:
            if counter == 1:
                url = base_url + urlArray[i]
                webpage2 = requests.get(url)
            else:
                url = base_url + urlArray[0].split(".htm")[0] + "-" + str(counter) + ".htm"
                webpage2 = requests.get(url)

            soup = BeautifulSoup(webpage2.content, "html.parser")

            a_tags = soup.find_all("a", {'class':"article-item block-item flex-column full-height"})

            count = 1
            artArray = []
            for a_tag in a_tags :
                artArray.append(str(a_tag["href"]))
                count += 1

            for j in range(0, len(artArray)):
                url = base_url + artArray[j]
                # print(url)
                web = requests.get(url)
                soup = BeautifulSoup(web.content, "html.parser")

                prices = soup.find('span', {'class':'d-block'})
                price = str(prices.getText().strip()).split("$")[1]
                images = soup.find('div', {'class':'js-lazy'})
                img = images['data-original']

                try:
                    reference1 = soup.find(class_ = 'col-md-12').find_all('tr')[2].get_text(strip=True)
                    reference2 = soup.select('td > a')[0].text
                    brand = soup.select('td > a')[1].text
                    model = soup.select('td > a')[2].text

                    details = soup.select('tr > td')
                    detail = soup.select('td > a')

                    if reference1[:16] == 'Reference number':
                        ref = str(reference1[16:])
                        brd = str(brand)
                        mdl = str(model)
                        prc = str(prices.getText().strip()).split("$")[1]
                        prc = int(prc.replace(',', ''))

                        dbInst = MySQLdb()
                        query = ''' SELECT * from tbl_crawl where brand=%s and model=%s and refNo=%s'''
                        existed_watch = dbInst.fetchOne(query, (brd, mdl, ref))
                        print('watch:',existed_watch)
                        if existed_watch is None:
                            print('add watch')
                            query2 = ''' INSERT INTO tbl_crawl(brand, model, refNo, price_chrono24, reg_time, img) values (%s, %s, %s, %s, %s, %s)'''
                            values2 = [brd, mdl, ref, prc, date.today(), img]
                        else:
                            print('update watch')
                            if existed_watch['img'] is None:
                                print('no img')
                                query2 = ''' UPDATE tbl_crawl set price_chrono24=%s, reg_time=%s, img=%s where brand=%s and model=%s and refNo=%s'''
                                values2 = [prc, date.today(),img, brd, mdl, ref]
                            else:
                                print('img exist')
                                query2 = ''' UPDATE tbl_crawl set price_chrono24=%s, reg_time=%s where brand=%s and model=%s and refNo=%s'''
                                values2 = [prc, date.today(), brd, mdl, ref]

                        dbInst.execute(query2, values2)
                        dbInst.disconnect()

                    # elif reference2[:2].isdigit() == True:
                    #     print('REFERENCE NUMBER:{}'.format(reference2))
                    #     print('BRAND:{}'.format(detail[1].text))
                    #     print('MODEL:{}'.format(detail[2].text))
                    #     print('CONDITION:{}'.format(details[0].text.strip()))
                    #     print('PRICE: '.format(prices.getText().strip()))
                    else:
                        #결과값중에 brand에서 춧자가 나타나면 brand값부터 reference number 순서대로 읽으면댐 price값은 맞음
                        pass
                except:
                    pass
                time.sleep(1)
