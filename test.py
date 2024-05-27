from sbx_search.search import SearchWrapper
client = SearchWrapper()
index = ['s0871-investments', 's0871-cons_units', 's0871-mandates', 's0871-ultimate_issuers', 's0871-cart', 's0871-country_of_risk']
# index = ['s0874-investments', 's0874-cons_units', 's0874-mandates', 's0874-ultimate_issuers', 's0874-cart', 's0874-country_of_risk']

res = client.search('bmw', index)

print(res)

# res = client.search('ald', 'cons_units')
#
# res = client.search('ald pimco', 'mandates')
# client.search('bockenheimer', ['investments', 'mandates', 'cons_units'], boosting={'mandates': 2.3, 'cons_units': 1.5}).to_dataframe()
#
# client.search('apple', ['s0871-investments', 's0871-mandates', 's0871-cons_units'], boosting={'s0871-mandates': 2.3, 's0871-cons_units': 1.5}, sort={'_score': 'desc', 'value': 'desc'}).to_dataframe()
#
#
# resp = client.get(index="instruments", id=1)