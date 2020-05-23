import re
import requests as req
import pandas as pd
from bs4 import BeautifulSoup as bs
from pprint import pprint


class ParserSuperJobVacancy:

    main_link = 'https://www.superjob.ru'

    add_link = '/vacancy/search'

    headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'}

    def get_response_text(self, params):
        try:
            responce = req.get(self.main_link + self.add_link, params=params, headers=self.headers)
            if responce.status_code == 200:
                return responce.text
        except Exception as ex:
            print('Exception in method get_response_text', ex)

    def get_vacancy_data(self, block):
        data = {}
        item_main_info = block.find('div', {'class': 'jNMYr GPKTZ _1tH7S'})
        if item_main_info:
            data['name'] = item_main_info.find('a').getText()
            data['ref'] = self.main_link + block.find('a')['href']
            data['mix_price'], data['max_price'], data['currency'] = self.get_price_data(item_main_info)
            emp_block = block.find('span', {'class': '_3mfro _3Fsn4 f-test-text-vacancy-item-company-name _9fXTd _2JVkc _2VHxz _15msI'})
            if emp_block:
                data['emp'] = emp_block.getText()

        return data

    def get_price_data(self, item_data):
        currency = None
        min_price = None
        max_price = None

        data = item_data.find('span', {'class': '_3mfro _2Wp8I _1qw9T f-test-text-company-item-salary PlM3e _2JVkc _2VHxz'})

        if data:
            try:
                str_price_data = data.getText()
                if str_price_data and str_price_data != 'По договорённости':
                    str_price_data = str_price_data.replace(" ", "").replace(u'\xa0', "")
                    price_data = re.split('—', str_price_data)
                    if len(price_data) > 1:
                        min_price = re.findall('\d+', price_data[0])[0]
                        max_price = re.findall('\d+', price_data[1])[0]
                    else:
                        if re.findall('от', price_data[0]):
                            min_price = re.findall('\d+', price_data[0])[0]
                        elif re.findall('до', price_data[0]):
                            max_price = re.findall('\d+', price_data[0])[0]

                    currency = re.findall('([a-zA-Zа-яА-Я]*\.?\s?[a-zA-Zа-яА-Я]+)\.?$', str_price_data)[0]
            except Exception as ex:
                print('Exception in method get_price_data', ex)

        if min_price:
            min_price = int(min_price)

        if max_price:
            max_price = int(max_price)

        return min_price, max_price, currency



    def parse_super_job(self, profession):
        params = {}
        params['keywords'] = profession

        prof_list = []

        while True:
            page = self.get_response_text(params)

            if not page:
                break

            soup = None

            soup = bs(page, 'lxml')
            block_list = soup.find_all('div', attrs={'class': 'iJCa5 f-test-vacancy-item _1fma_ _1JhPh _2gFpt _1znz6 _2nteL'})
            for block in block_list:
                data_dict = self.get_vacancy_data(block)

                if data_dict:
                    prof_list.append(data_dict)

            next_page_button = soup.find('a', {'class': 'icMQ_ _1_Cht _3ze9n f-test-button-dalshe f-test-link-Dalshe'})
            if not next_page_button:
                break
            else:
                link = next_page_button['href']
                num_page = re.findall('&page=(\d+)', link)[0]
                if not num_page:
                    break
                else:
                    params['page'] = num_page

        return prof_list


if __name__ == '__main__':
    profession = input('Введите проффессию: ')

    if profession:
        parser = ParserSuperJobVacancy()
        list_data = parser.parse_super_job(profession)

        if len(list_data) > 0:
            df = pd.DataFrame(list_data)
            pprint(df)