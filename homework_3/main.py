import re
import requests as req
import pandas as pd
from pprint import pprint
from bs4 import BeautifulSoup as bs
from pymongo import MongoClient
from pycbrf.toolbox import ExchangeRates
import datetime


class ParserHHVacancy:

    main_link = 'https://hh.ru'

    add_link = '/search/vacancy'

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'}

    col_name = 'name'
    col_id = 'id'
    col_price_min = 'price_min'
    col_price_max = 'price_max'
    col_ref = 'ref'
    col_emp = 'emp'
    col_currency = 'currency'

    collection = None

    def __init__(self):
        self.initDb = InitializerVacancyDb()
        self.collection = self.initDb.get_collection("hh_vacancy")

    @classmethod
    def get_response_text(self, params):
        try:
            responce = req.get(self.main_link + self.add_link, params=params, headers=self.headers)
            if responce.status_code == 200:
                return responce.text
        except Exception as ex:
            print('Exception in method get_response_text', ex)

    @staticmethod
    def get_price_data(price_string):
        min_value = None
        max_value = None
        try:
            if price_string:
                price = price_string.replace(" ", "").replace(u'\xa0', "")

                price_data = re.split('-', price)
                if len(price_data) > 1:
                    min_value = re.match('\d+', price_data[0]).group(0)
                    max_value = re.match('\d+', price_data[1]).group(0)
                else:
                    if re.findall('от', price_data[0]):
                        min_value = re.findall('\d+', price_data[0])[0]
                        max_value = None
                    elif re.findall('до', price_data[0]):
                        min_value = None
                        max_value = re.findall('\d+', price_data[0])[0]

        except Exception as ex:
            print('Exception in method get_price_data', ex)

        if min_value:
            min_value = int(min_value)

        if max_value:
            max_value = int(max_value)

        return min_value, max_value

    @staticmethod
    def get_currency(price_string):
        if price_string:
            return re.findall('([a-zA-Zа-яА-Я]*\.?\s?[a-zA-Zа-яА-Я]+)\.?$', price_string)[0].replace(' ', '')

    def get_block_data(self, prof_name, prof_price, prof_emp):
        prof_dict = {}

        try:
            prof_dict[self.col_name] = prof_name.getText()
            prof_dict[self.col_ref] = prof_name['href']
            prof_dict[self.col_id] = re.findall('hh.ru/vacancy/(\d+)', prof_dict[self.col_ref])[0]
            price_str = prof_price.getText()
            prof_dict[self.col_price_min], prof_dict[self.col_price_max] = ParserHHVacancy.get_price_data(price_str)
            prof_dict[self.col_currency] = ParserHHVacancy.get_currency(price_str)
            prof_dict[self.col_emp] = prof_emp.getText()
        except Exception as ex:
            print('Exception in method get_block_data', ex)

        return prof_dict

    def add_vacancy_to_db(self, prof_dict):
        try:
            elem = self.collection.find_one({self.col_id: prof_dict[self.col_id]})
            if not elem:
                self.collection.insert_one({
                    self.col_id: prof_dict[self.col_id],
                    self.col_name: prof_dict[self.col_name],
                    self.col_ref: prof_dict[self.col_ref],
                    self.col_emp: prof_dict[self.col_emp],
                    self.col_price_min: prof_dict[self.col_price_min],
                    self.col_price_max: prof_dict[self.col_price_max],
                    self.col_currency: prof_dict[self.col_currency]
                })
            else:
                for col, value in elem.items():
                    if col == '_id':
                        continue

                    if value != prof_dict[col]:
                        self.collection.updateOne({self.col_id: prof_dict[self.col_id]}, {col: prof_dict[col]})

        except Exception as ex:
            print('Exception in method add_vacancy_to_db', ex)

    def parse_hh(self, profession):
        params = {}
        params['text'] = profession

        prof_list = []

        while True:
            page = self.get_response_text(params)

            if not page:
                break

            soup = bs(page, 'lxml')
            blocks_list = soup.find('div', {'class': 'vacancy-serp'})

            for block in blocks_list:

                item_prof_name = block.find('a', {'class': 'bloko-link HH-LinkModifier'})
                item_prof_price = block.find('div', {'class': 'vacancy-serp-item__sidebar'})
                item_prof_emp = block.find('div', {'class': 'vacancy-serp-item__meta-info'})

                if item_prof_name and item_prof_price and item_prof_emp:
                    prof_dict = {}
                    prof_dict = self.get_block_data(item_prof_name, item_prof_price, item_prof_emp)
                    prof_list.append(prof_dict)

                    self.add_vacancy_to_db(prof_dict)

            next_page = soup.find('a', {'class': 'bloko-button HH-Pager-Controls-Next HH-Pager-Control'})

            if not next_page:
                break
            else:
                params['page'] = next_page['data-page']

        print(len(prof_list))
        if len(prof_list) > 0:
            df = pd.DataFrame(prof_list)
            return df


class DbServices:

    def __init__(self):
        initDb = InitializerVacancyDb()
        self.collection = initDb.get_collection("hh_vacancy")
        now = datetime.datetime.now().strftime("%Y-%m-%d")
        self.rates = ExchangeRates(now)

    def show_vacancy_by_salary(self, salary):
        try:
            list = self.collection.find(
            {
                '$or':
                    [
                        {
                            '$and':
                                [
                                    {'currency': 'руб'},
                                    {
                                        '$or':
                                            [
                                                {'price_min': {'$gt': salary}},
                                                {'price_max': {'$gt': salary}}
                                            ]
                                    }
                                ]
                        },
                        {
                            '$and':
                                [
                                    {'currency': 'USD'},
                                    {
                                        '$or':
                                            [
                                                {'price_min': {'$gt': int(salary / self.rates['USD'].value)}},
                                                {'price_max': {'$gt': int(salary / self.rates['USD'].value)}}
                                            ]
                                    }
                                ]
                        },
                        {
                            '$and':
                                [
                                    {'currency': 'KZT'},
                                    {
                                        '$or':
                                            [
                                                {'price_min': {'$gt': int(salary / self.rates['KZT'].value)}},
                                                {'price_max': {'$gt': int(salary / self.rates['KZT'].value)}}
                                            ]
                                    }
                                ]
                        },
                        {
                            '$and':
                                [
                                    {'currency': 'грн'},
                                    {
                                        '$or':
                                            [
                                                {'price_min': {'$gt': int(salary / self.rates['UAH'].value)}},
                                                {'price_max': {'$gt': int(salary / self.rates['UAH'].value)}}
                                            ]
                                    }
                                ]
                        },
                        {
                            '$and':
                                [
                                    {'currency': 'бел.руб'},
                                    {
                                        '$or':
                                            [
                                                {'price_min': {'$gt': int(salary / self.rates['BYN'].value)}},
                                                {'price_max': {'$gt': int(salary / self.rates['BYN'].value)}}
                                            ]
                                    }
                                ]
                        },
                        {
                            '$and':
                                [
                                    {'currency': 'EUR'},
                                    {
                                        '$or':
                                            [
                                                {'price_min': {'$gt': int(salary / self.rates['EUR'].value)}},
                                                {'price_max': {'$gt': int(salary / self.rates['EUR'].value)}}
                                            ]
                                    }
                                ]
                        }
                    ]
            })

            for item in list:
                print(item)
        except Exception as ex:
            print('Exception in method show_vacancy_by_salary', ex)


class InitializerVacancyDb:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client['vacancy']

    def get_collection(self, name):
        return self.db[name]


if __name__ == '__main__':
    profession = input('Введите проффессию: ')

    if profession:
        parser = ParserHHVacancy()
        df = parser.parse_hh(profession)

    salary = int(input('Введите минимальную цену: '))

    if salary:
        service = DbServices()
        service.show_vacancy_by_salary(salary)


