from sbx_search import SearchWrapper, SearchResults
# This script is old and need to be update according to search.py
# Recommend to debug using example_search.py or test.py

client = SearchWrapper()
def _indexname(index_type: str, portfolio: str):
    return f'{portfolio.lower()}-{index_type}'

def _normalize_indices(search_results: SearchResults):
    for res in search_results.results:
        res.index = res.index.split('-')[-1]

q = "allianz"
indices= [
        'investments',
        'cons_units',
        'mandates',
        'ultimate_issuers',
        'cart',
        'country_of_risk'
    ]
portfolio = 'S0871'

index_names = [_indexname(index, portfolio) for index in indices]
res = client.search(
    q,
    index_names,
    boosting={
        _indexname('mandates', portfolio): 2.3,
        _indexname('cons_units', portfolio): 2.3,
        _indexname('ultimate_issuers', portfolio): 2.3,
        _indexname('cart', portfolio): 13.3,
        _indexname('country_of_risk', portfolio): 4.3
    },
    sort={
        '_score': 'desc',
        'value': 'desc'
    }
)
_normalize_indices(res)
print(res.to_dict())