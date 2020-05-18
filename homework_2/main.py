from bs4 import BeautifulSoup as bs
import requests as req
from pprint import pprint
import re
import pandas as pd


main_link = 'https://hh.ru'
add_link = '/search/vacancy'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'}


def get_response_text(params):
    responce = req.get(main_link + add_link, params=params, headers=headers)
    if responce.status_code == 200:
        return responce.text


def get_city_id(city_name, city_list):
    if city_input:
        for city in city_list:
            if city['city_name'] == city_name:
                return city['city_id']


def get_available_list_city(page):
    city_list = []

    try:
        soup = bs(page, 'lxml')
        items = soup.find('div', {'class': 'clusters-group__items'}).findAll('a', {'class': 'clusters-value'})

        for city in items:
            city_dict = {}
            city_ref = city['href']
            city_dict['city_id'] = re.findall('&area=(\d*)&', city_ref)[0]
            city_dict['city_name'] = city.find('span', {'class': 'clusters-value__name'}).getText()
            city_list.append(city_dict)
    except Exception as ex:
        print('Exception in method get_available_list_city', ex)

    return city_list


def get_price_data(price_string):
    min_value = 0
    max_value = 0

    if price_string:
        price = price_string.replace(" ", "").replace(u'\xa0', "")

        price_data = re.split('-', price)
        if len(price_data) > 1:
            min_value = re.match('\d+', price_data[0]).group(0)
            max_value = re.match('\d+', price_data[1]).group(0)
        else:
            if re.findall('от', price_data[0]):
                min_value = re.findall('\d+', price_data[0])[0]
                max_value = 0
            elif re.findall('до', price_data[0]):
                min_value = 0
                max_value = re.findall('\d+', price_data[0])[0]

    return min_value, max_value


def get_currency(price_string):
    if price_string:
        return re.findall('([a-zA-Zа-яА-Я]+)\.?$', price_string)


def print_full(x):
    pd.set_option('display.max_rows', len(x))
    pd.set_option('display.max_columns', 10)
    pprint(x)
    pd.reset_option('display.max_rows')
    pd.reset_option('display.max_columns')


params = {}
profession = input('Введите проффессию: ')

if profession:
    params['text'] = profession
    page = get_response_text(params)

    if page:

        city_list = get_available_list_city(page)

        if len(city_list) > 0:
            city_input = input('Введите город: ')
            city_id = get_city_id(city_input, city_list)

            if city_id:
                params['area'] = city_id
            else:
                print('Города с такой вакансией нет! Поиск будет производиться по всем городам России')


        salary_input = input('Установите минимальную зарплату: ')

        if salary_input.isdigit():
            params['salary'] = salary_input
        else:
            print('Минимальная зп не введена!')

        prof_list = []

        while True:
            page = get_response_text(params)

            if not page:
                break

            soup = bs(page, 'lxml')
            items = soup.find('div', {'class': 'vacancy-serp'})

            for item in items:
                prof_dict = {}

                item_prof_name = item.find('a', {'class': 'bloko-link HH-LinkModifier'})
                item_prof_price = item.find('div', {'class': 'vacancy-serp-item__sidebar'})
                item_prof_emp = item.find('div', {'class': 'vacancy-serp-item__meta-info'})

                if item_prof_name and item_prof_price and item_prof_emp:
                    prof_dict['name'] = item_prof_name.getText()
                    prof_dict['ref'] = item_prof_name['href']
                    price_str = item_prof_price.getText()
                    prof_dict['price_min'], prof_dict['price_max'] = get_price_data(price_str)
                    prof_dict['currency'] = get_currency(price_str)
                    prof_dict['emp'] = item_prof_emp.getText()
                    prof_list.append(prof_dict)

            next_page = soup.find('a', {'class': 'bloko-button HH-Pager-Controls-Next HH-Pager-Control'})

            if not next_page:
                break
            else:
                params['page'] = next_page['data-page']

        print(len(prof_list))
        df = pd.DataFrame(prof_list)
        print_full(df)
