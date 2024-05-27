import json
import requests
from datetime import date
from config import portfolio_codes
from load_portfolios import (
    ElasticsearchDatabaseReader, ElasticsearchFileReaderTypes,
    ElasticsearchFileReader, ElasticsearchPortfolioDataReader)

reader = ElasticsearchDatabaseReader('S0871', date(2022, 10, 31))
reader.read()
inv_input = reader.get_investment_input()