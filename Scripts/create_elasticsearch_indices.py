import requests
from config import portfolio_codes, indices
import json

with open('elastic_config_local.json') as f:
    elastic_config = json.load(f)
    pw = elastic_config["password"]
    user = elastic_config["user"]
    base_url = elastic_config["base_url"]

indices = indices

contents = open('create_index.json', 'rb').read()
for index in indices:
    for portfolio in portfolio_codes:
        print(f'Deleting index {index} for {portfolio}')
        res = requests.delete(
            f'{base_url}/{portfolio}-{index}',
            headers={'Content-Type': 'application/json'},
            auth=(user, pw)
        )
        print(f'Deleting response:{res.content}')
        print(f'Creating index {index} for {portfolio}')
        res = requests.put(
            f'{base_url}/{portfolio}-{index}', headers={'Content-Type': 'application/json'},
            auth=(user, pw), data=contents)
        print(f'Creating response: {res.content}')

        res = requests.get(f'{base_url}/{portfolio}-{index}', headers={'Content-Type': 'application/json'},
                           auth=(user, pw))
        print(f'get response: {res.content}')
    print(res.content)
