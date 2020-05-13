import requests
import json
from pprint import pprint


def get_link():
    user_name = input()
    user_name = user_name if user_name else 'Hadirback'
    return f'https://api.github.com/users/{user_name}/repos'


main_link = get_link()

header = { 'Accept':'application/vnd.github.nebula-preview+json' }

response = requests.get(main_link, headers=header)

if response.ok:
    print(type(response.text))
    data = json.loads(response.text)
    for repos_info in data:
        print(repos_info['name'])

    with open('repos.json', 'w') as f:
        json.dump(data, f)

