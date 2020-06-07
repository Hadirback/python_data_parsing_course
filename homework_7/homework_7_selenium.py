from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient
import hashlib
import datetime


def get_month(string_month):
    month = None
    if string_month == 'января':
        month = '01'
    elif string_month == 'февраля':
        month = '02'
    elif string_month == 'марта':
        month = '03'
    elif string_month == 'апреля':
        month = '04'
    elif string_month == 'мая':
        month = '05'
    elif string_month == 'июня':
        month = '06'
    elif string_month == 'июля':
        month = '07'
    elif string_month == 'августа':
        month = '08'
    elif string_month == 'сентрября':
        month = '09'
    elif string_month == 'октября':
        month = '10'
    elif string_month == 'ноября':
        month = '11'
    elif string_month == 'декабря':
        month = '12'
    else:
        month = '01'
    return month


def forrmated_date(date_string):
    datetime_parts = date_string.split(',')

    if not date_string:
        return None

    date_result = None
    time = datetime_parts[1].replace(" ", "")
    if datetime_parts[0] == 'Сегодня':
        date_result = f'{datetime.datetime.now().strftime("%Y-%m-%d")} {time}'
    elif datetime_parts[0] == 'Вчера':
        yesterday_date = datetime.datetime.now() - datetime.timedelta(days=1)
        date_result = f'{yesterday_date.strftime("%Y-%m-%d")} {time}'
    else:
        date_parts = datetime_parts[0].split(' ')
        day = '{:02}'.format(int(date_parts[0]))
        month = get_month(date_parts[1])
        year = None
        if not date_parts[2]:
            year = datetime.datetime.now().strftime("%Y")
        else:
            year = date_parts[2]
        date_result = f'{year}-{month}-{day} {time}'
    return date_result


class EmailParseSelenium:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        db = client.emails
        self.collection = db['mailru']
        self.driver = webdriver.Chrome()
        self.authentification_mailru('study.ai_172@mail.ru', 'NextPassword172')

    def authentification_mailru(self, login, password):
        self.driver.get('https://mail.ru')
        elem = self.driver.find_element_by_id('mailbox:login')
        elem.send_keys(login)

        elem_button = self.driver.find_element_by_id('mailbox:submit')
        elem_button.click()

        wait = WebDriverWait(self.driver, 10)

        elem_pass = wait.until(EC.element_to_be_clickable((By.ID, 'mailbox:password')))
        elem_pass.send_keys(password)

        elem_button = self.driver.find_element_by_id('mailbox:submit')
        elem_button.click()

    def get_links(self):
        links = set()
        last_elem = None
        scr1 = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH,
                                        '//div[contains(@class, "scrollable g-scrollable scrollable_bright scrollable_footer")]')))

        while True:
            try:
                current_emails = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, '//a[contains(@class,"js-letter-list-item")]')))

                if not current_emails:
                    break

                if last_elem == current_emails[-1]:
                    break

                last_elem = current_emails[-1]
                [links.add(mail.get_attribute('href')) for mail in current_emails]

                self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scr1)
            except Exception as ex:
                print(ex)
                break

        return links

    def save_into_db(self, id, title, sender_name, sender_email, body, date):
        self.collection.update_one({'_id': id}, {'$set': {'title': title, 'sender_name': sender_name,
                                                  'sender_email': sender_email, 'body': body, 'date': date}}, upsert=True)

    def init(self):
        links = self.get_links()
        for link in links:
            try:
                self.driver.get(link)
                hash_object = hashlib.md5(link.encode('utf-8'))
                id = hash_object.hexdigest()
                title = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//h2[contains(@class, "thread__subject")]'))).text
                sender_name = self.driver.find_element_by_xpath('//div[@class="letter__author"]/span').text
                sender_email = self.driver.find_element_by_xpath('//div[@class="letter__author"]/span').get_attribute('title')
                body = self.driver.find_element_by_xpath('//div[contains(@class, "letter__body")]').text
                date = self.driver.find_element_by_xpath('//div[contains(@class, "letter__date")]').text
                if date:
                    date = forrmated_date(date)

                self.save_into_db(id, title, sender_name, sender_email, body, date)
            except Exception as ex:
                print(ex)


if __name__ == '__main__':
    selenium_parser = EmailParseSelenium()
    selenium_parser.init()