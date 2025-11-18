import re
import time
import pymysql
from os import environ

class MySQLdb:
    def __init__(self):
        self.connection = None
        self.connect()

    def connect(self):
        if self.connection is None:
            self.connection= pymysql.connect(
                host='canvas-main.mysql.database.azure.com',
                user='user',
                password='pwd',
                db='db',
                port=3306,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                ssl={'ssl':{'ca':'C:\BaltimoreCyberTrustRoot.crt'}}
                )
        print('connected')

    def execute(self, query, values):
        with self.connection.cursor() as cursor:
            result = cursor.execute(query, values) 
            self.connection.commit()
            affected = f"{cursor.rowcount} rows affected."
            print('affected: ',affected)
            cursor.close()
            return affected
 
    def fetchOne(self, query, values):
        with self.connection.cursor() as cursor:
            cursor.execute(query, values)
            result = cursor.fetchone()
            cursor.close()
            return result
 
    def fetchAll(self, query, values):
        with self.connection.cursor() as cursor:
            cursor.execute(query, values)
            result= cursor.fetchall()
            cursor.close()
            return result
 
    def disconnect(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None

        print('disconnected')

class CrawlFunction:
    def emitDollar(price):
        return int(price.replace('.00', '').replace(',', '').replace('$', ''))
    
    def isNextBtn(element):
        return element.get_attribute('class') == 'next page-numbers'

    def findValue(element):
        return element.find_element_by_tag_name('a').text

    def findHref(element):
        return element.find_element_by_tag_name('a').get_attribute('href')

    def isPicto(element):
        return len(element.find_elements_by_class_name('picto')) > 0

    def isProduct(element):
        return element.get_attribute('class').startswith('product type-product status-publish ')

    def isOverflow(element):
        return element.get_attribute('class').startswith(' ')

    def camelCase(string):
        string = re.sub(r"(_|-)+.", " ", string).title().replace(" ", "")
        return string[0].lower() + string[1:]

    def isHref(element):
        try:
            element.find_element_by_tag_name('a').get_attribute('href')
            return True
        except:
            return False

    def scrollDown(driver):
        SCROLL_PAUSE_TIME = 1
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        return last_height

    def ifExist(title_list, string, watch_dict):
        for item in title_list:
            if item in string:
                new_str = string.replace(item+'\u2003', '')
                new_str = new_str.replace('\u2019', '')
                camel = camelCase(item)
                watch_dict[camel] = new_str
