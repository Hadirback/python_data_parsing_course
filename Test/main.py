import re
from pymongo import MongoClient
from pprint import pprint
from pycbrf.toolbox import ExchangeRates
import datetime


client = MongoClient('localhost', 27017)
db = client['vacancy']
hh = db.hh_vacancy

#hh.delete_many({})

salary = 10000

now = datetime.datetime.now().strftime("%Y-%m-%d")
rates = ExchangeRates(now)
print(rates['KZT'].value)

list = hh.find(
{
    '$or' :
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
                        {'price_min': {'$gt': int(salary / rates['USD'].value)}},
                        {'price_max': {'$gt': int(salary / rates['USD'].value)}}
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
                        {'price_min': {'$gt': int(salary / rates['KZT'].value)}},
                        {'price_max': {'$gt': int(salary / rates['KZT'].value)}}
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
                        {'price_min': {'$gt': int(salary / rates['UAH'].value)}},
                        {'price_max': {'$gt': int(salary / rates['UAH'].value)}}
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
                        {'price_min': {'$gt': int(salary / rates['BYN'].value)}},
                        {'price_max': {'$gt': int(salary / rates['BYN'].value)}}
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
                        {'price_min': {'$gt': int(salary / rates['EUR'].value)}},
                        {'price_max': {'$gt': int(salary / rates['EUR'].value)}}
                    ]
                }
            ]
        }
    ]
})

print(list.count())

#for item in list:
    #print(item)
#print(list.count())

#string = 'до 34 5345 бел руб.'
#print(re.findall('([a-zA-Zа-яА-Я]*\.?\s?[a-zA-Zа-яА-Я]+)\.?$', string)[0])





print(rates['KZT'].value)
