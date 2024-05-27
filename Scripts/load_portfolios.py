import pandas as pd
import cx_Oracle
from db_connection import create_oracle_engine
from sqlalchemy import MetaData, Table
from sqlalchemy.sql import select, and_
from datetime import date
from enum import Enum
from typing import Callable
from abc import ABC, abstractmethod
cx_Oracle.init_oracle_client(lib_dir='C:/Oracle/OraClientEXA/OraClient193_64/')


class Measure:
    attribute: str
    caption: str

    def __init__(self, attribute, caption):
        self.attribute = attribute
        self.caption = caption


class Measures:
    market_value = Measure('market_value_dirty_eur', 'Market Value Dirty (EUR)')
    exposure = Measure('exposure_eur', 'Exposure (EUR)')
    notional = Measure('notional_eur', 'Notional (EUR)')


class ElasticsearchPortfolioDataReader(ABC):

    MEASURE_NAME = 'value'
    MEASURE_TYPE_NAME = 'value_type'

    df: pd.DataFrame

    @abstractmethod
    def read(self):
        pass

    def _aggregate_measure(self, qualitative_attributes, measure):
        res_df = self.df[qualitative_attributes + [measure.attribute]].groupby(
            qualitative_attributes).sum().reset_index()
        res_df.loc[:, self.MEASURE_TYPE_NAME] = measure.caption
        res_df.rename({measure.attribute: self.MEASURE_NAME}, axis=1, inplace=True)
        return res_df

    def get_investment_input(self):

        qualitative_attributes = [
            'standardized_investment_name',
        ]
        unique_attribute = 'sink_id'
        quantitative_attributes = [
            'market_value_dirty_eur']

        # filter out lines that are zero for all quantitative columns
        inv_input = self.df.loc[self.df[quantitative_attributes].abs().sum(axis=1) > 0]

        # filter out consolidated entries if not already filtered out
        mask = ((inv_input['consolidation_flag'] == 'N') & (inv_input['exposure_adjustment_code_l2'] == 'UNADJ'))
        inv_input = inv_input.loc[mask]

        # define new exposure attribute, take notional if derivative, otherwise market value
        mask = inv_input['sityids_code'].str.startswith('X')
        inv_input.loc[~mask, self.MEASURE_NAME] = inv_input.loc[:, Measures.market_value.attribute]
        inv_input.loc[~mask, self.MEASURE_TYPE_NAME] = Measures.market_value.caption
        inv_input.loc[mask, self.MEASURE_NAME] = inv_input.loc[mask, Measures.notional.attribute]
        inv_input.loc[mask, self.MEASURE_TYPE_NAME] = Measures.notional.caption

        inv_input = inv_input[qualitative_attributes + [self.MEASURE_NAME, self.MEASURE_TYPE_NAME]].groupby(
            qualitative_attributes).sum().reset_index()

        # remove duplicates
        mask = ~(
            (inv_input[unique_attribute].duplicated(False)) &
            (inv_input[self.MEASURE_NAME] == 0)
        )
        inv_input = inv_input.loc[mask, :]

        # create artificial id column
        inv_input.loc[:, 'position_id'] = inv_input.index

        return inv_input

    def get_cons_unit_input(self):
        qualitative_attributes = ['cons_unit_code', 'cons_unit_name']
        measure = Measures.exposure
        return self._aggregate_measure(qualitative_attributes, measure)

    def get_mandate_input(self):
        qualtiative_attributes = ['local_portfolio_l5']
        measure = Measures.exposure
        return self._aggregate_measure(qualtiative_attributes, measure)

    def get_ultimate_issuer_input(self):
        qualitative_attributes = ['ultimate_issuer']
        measure = Measures.exposure
        return self._aggregate_measure(qualitative_attributes, measure)

    def get_country_input(self):
        qualitative_attributes = ['country_of_risk']
        measure = Measures.exposure
        return self._aggregate_measure(qualitative_attributes, measure)

    def get_cart_input(self):
        cart_attributes = ['cart_l1']
        measure = Measures.exposure
        dfs = []
        for cart in cart_attributes:
            df = self._aggregate_measure([cart], measure)
            df = df.rename({cart: 'cart'}, axis=1)
            dfs.append(df)
        return pd.concat(dfs)


class ElasticsearchDatabaseReader(ElasticsearchPortfolioDataReader):

    def __init__(
        self,
        portfolio_code: str,
        date: date,
        schema: str,
        dataset: str,
        table_name: str,
        database_config_file: str = 'oracle_config.json',

    ):

        self.portfolio_code = portfolio_code
        self.date = date
        self.schema = schema
        self.dataset = dataset
        self.database_config_file = database_config_file
        self.table_name = table_name

    def read(self):
        oc_engine = create_oracle_engine(database_config_file=self.database_config_file)
        oc_metadata = MetaData(bind=oc_engine, schema=self.schema)
        oc_table = Table(self.table_name, oc_metadata, autoload=True)
        oc_columns = [
            oc_table.c.snode_name,
        ]

        self.df = _read_portfolio(
            oc_engine, oc_table, self.date, self.dataset, self.portfolio_code, oc_columns)


class ElasticsearchFileReaderTypes(Enum):
    CSV = 1
    EXCEL = 2


class ElasticsearchFileReader(ElasticsearchPortfolioDataReader):

    def __init__(self, filename: str, filetype: ElasticsearchFileReaderTypes):
        self.filename: str = filename
        self.filetype: str = filetype
        self.read_func: Callable
        if filetype == ElasticsearchFileReaderTypes.CSV:
            self.read_func: callable = getattr(pd, 'read_csv')
        elif filetype == ElasticsearchFileReaderTypes.EXCEL:
            self.read_func = getattr(pd, 'read_excel')
        else:
            raise ValueError('Only CSV and Excel supported.')

    def read(self):
        self.df = self.read_func(self.filename)


def _read_portfolio(oc_engine, oc_table, date_value, dataset, portfolio_code, oc_columns):
    # print(f'Reading dataframe from Oracle table: {date_value}')

    # query to fetch the available data from the Oracle database
    s = select(oc_columns).where(
        and_(
            oc_table.c.reporting_date == date_value,
        )
    )
    df = pd.read_sql(s, oc_engine)
    return df
