import requests
from pprint import  pprint
import json

main_link = 'https://api.alibraonline.ru/api/v1/users/auth/'
header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
          'Accept':'application/json',
          'Content-Type': 'application/json'}

params = {'username':'',
          'password':''}

response = requests.post(main_link,headers=header,data=json.dumps(params))

if response.ok:
    pprint(response.text)

    text = f'response.ok - {response.ok} \n response.status_code - {response.status_code} \n response.text - {response.text}'
    with open('repos.txt', 'w') as f:
        f.write(text)
