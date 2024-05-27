import requests
import json
with open('elastic_config_local.json') as f:
    elastic_config = json.load(f)
    pw = elastic_config["password"]
    user = elastic_config["user"]
    base_url = elastic_config["base_url"]

# test using search query from json file
contents = open('example_search.json', 'rb').read()
res = requests.post('http://localhost:9200/investments/_search', headers={'Content-Type': 'application/json'}, auth=(user, pw), data=contents)
print(json.loads(res.content))

# test tokenizer fron json file
content = open('tokenizer_content.json', 'rb').read()
res = requests.post('http://localhost:9200/_search', headers={'Content-Type': 'application/json'}, auth=(user, pw), data=content)
print(json.loads(res.content))

# get the tokens from specific analyzer
contents = '{  "analyzer": "default","text": "ALLIANZ DLVR FONDS INHABER-ANTEILE Allianz DLVR Fonds Inhaber-Anteile Allianz DLVR Fonds Inhaber-Anteile Allianz DLVR Fonds Inhaber-Anteile not defined Deutsche Lebensvers.-AG DE - Germany Alternatives/Other Not listed Equity (including participations) Not listed Equity (including participations) unconstrained " }'
res = requests.post('http://localhost:9200/s0874-ultimate_issuers/_analyze', headers={'Content-Type': 'application/json'}, auth=(user, pw), data=contents)
print(json.loads(res.content))

# list all the index
res = requests.get('http://localhost:9200/_cat/indices/?v=true&s=index', auth=(user, pw))
print(res.content)

