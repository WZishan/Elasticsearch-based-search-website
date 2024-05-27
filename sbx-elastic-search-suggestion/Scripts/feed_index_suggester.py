import json
import requests
from datetime import date
from config import portfolio_codes
from load_portfolios import (
    ElasticsearchDatabaseReader, ElasticsearchFileReaderTypes,
    ElasticsearchFileReader, ElasticsearchPortfolioDataReader)
from sbx_search.config.search_attributes_mapping import get_default_attributes

with open('elastic_config_local.json') as f:
    elastic_config = json.load(f)
    elastic_password = elastic_config["password"]
    elastic_user = elastic_config["user"]
    base_url = elastic_config["base_url"]

# generator function for creating batches
def batches(lst, batch_size=1):

    for i in range(0, len(lst), batch_size):
        yield lst[i:i + batch_size]


def create_input_from_dict(data: dict, id_col: str, attributes: list[str]) -> str:
    inputList = []
    for d in data:
        valuesList = []
        for key in d.keys():
            if key in attributes:
                valuesList.append(d[key])
        #
        d["title"] = valuesList
        # add record type as keyword
        d['title'].append(id_col)
        input = f'{{"index": {{"_id": {json.dumps(d[id_col])}}}}}\n{json.dumps(d)}'
        inputList.append(input)
    elasticsearch_input = '\n'.join(inputList) + "\n"
    return elasticsearch_input


def push_data(base_url, index, data, user='elastic', password=''):
    response = requests.post(
        f'{base_url}/{index}/_bulk?pretty&refresh',
        auth=(user, password),
        data=data,
        headers={
            'Content-Type': 'application/json'
        })
    # raise error in case something goes wrong
    response.raise_for_status()


def fill_investment_index(reader: ElasticsearchPortfolioDataReader, portfolio_code: str):
    positions_df = reader.get_investment_input()
    positions = positions_df.to_dict('records')

    batch_size = 5000
    num_batches = int((len(positions) - 1) / batch_size) + 1
    batch_cnt = 1
    attributes = get_default_attributes("investments")
    for batch in batches(positions, batch_size=5000):

        print(f'Starting batch {batch_cnt} of {num_batches}')
        elasticsearch_input = create_input_from_dict(batch, 'position_id',attributes)

        try:
            push_data(
                base_url,
                f'{portfolio_code}-investments',
                elasticsearch_input,
                elastic_user,
                elastic_password)
            print('...done')
            batch_cnt += 1
        except requests.exceptions.HTTPError as err:
            print(err)
            exit()


def fill_cons_unit_index(reader: ElasticsearchPortfolioDataReader, portfolio_code: str):
    cons_units = reader.get_cons_unit_input().to_dict('records')
    attributes = get_default_attributes("cons_units")
    elasticsearch_input = create_input_from_dict(cons_units, 'cons_unit_code',attributes)
    try:
        push_data(
            base_url, f'{portfolio_code}-cons_units',
            elasticsearch_input, elastic_user, elastic_password)
    except requests.exceptions.HTTPError as err:
        print(err)


def fill_mandate_index(reader: ElasticsearchPortfolioDataReader, portfolio_code: str):
    mandates = reader.get_mandate_input().to_dict('records')
    attributes = get_default_attributes("mandates")
    elasticsearch_input = create_input_from_dict(mandates, 'local_portfolio_l5',attributes)
    try:
        push_data(
            base_url, f'{portfolio_code}-mandates',
            elasticsearch_input, elastic_user, elastic_password)
    except requests.exceptions.HTTPError as err:
        print(err)


def fill_issuer_index(reader: ElasticsearchPortfolioDataReader, portfolio_code: str):
    ultimate_issuers = reader.get_ultimate_issuer_input().to_dict('records')
    attributes = get_default_attributes("ultimate_issuers")
    elasticsearch_input = create_input_from_dict(ultimate_issuers, 'ultimate_issuer',attributes)
    try:
        push_data(
            base_url, f'{portfolio_code}-ultimate_issuers',
            elasticsearch_input, elastic_user, elastic_password
        )
    except requests.exceptions.HTTPError as err:
        print(err)


def fill_country_index(reader: ElasticsearchPortfolioDataReader, portfolio_code: str):
    countries = reader.get_country_input().to_dict('records')
    attributes = get_default_attributes("country_of_risk")
    elasticsearch_input = create_input_from_dict(countries, 'country_of_risk',attributes)
    try:
        push_data(
            base_url, f'{portfolio_code}-country_of_risk',
            elasticsearch_input, elastic_user, elastic_password
        )
    except requests.exceptions.HTTPError as err:
        print(err)


def fill_cart_index(reader: ElasticsearchPortfolioDataReader, portfolio_code: str):
    cart_data = reader.get_cart_input().to_dict('records')
    attributes = get_default_attributes("cart")
    elasticsearch_input = create_input_from_dict(cart_data, 'cart', attributes)
    try:
        push_data(
            base_url, f'{portfolio_code}-cart',
            elasticsearch_input, elastic_user, elastic_password
        )
    except requests.exceptions.HTTPError as err:
        print(err)


def main():
    data_date = date(2024, 3, 31)
    for portfolio in portfolio_codes:
        print(f'Starting {portfolio}')
        if portfolio == 'pfp':
            reader = ElasticsearchFileReader(
                'pfp_scope_look_through.xlsx',
                ElasticsearchFileReaderTypes.EXCEL)
            reader.read()
            fill_investment_index(reader, portfolio)
        else:
            reader = ElasticsearchDatabaseReader(portfolio.upper(),data_date)
            reader.read()
            fill_investment_index(reader, portfolio)
            fill_cons_unit_index(reader, portfolio)
            fill_mandate_index(reader, portfolio)
            fill_issuer_index(reader, portfolio)
            fill_cart_index(reader, portfolio)
            fill_country_index(reader, portfolio)
        print(f'... finished {portfolio}')


if __name__ == '__main__':
    main()
