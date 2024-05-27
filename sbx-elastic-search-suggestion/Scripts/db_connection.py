import psycopg2

from db_config import OracleDatabaseConfig, PostgreDatabaseConfig
from sqlalchemy import create_engine
import cx_Oracle as cx
import os
from getpass import getpass


def create_oracle_engine(database_config_file='db_config.json'):

    # read the config
    config = OracleDatabaseConfig(database_config_file)

    # generate connection string
    if 'user' in config and 'password' in config:
        connection_string = make_oracle_connection_string(
            config.user,
            config.password,
            config.host,
            config.service_name
        )
    else:
        # lets ask the user for his database password
        user = os.getlogin()
        password = getpass(f'Database Password for {user} on {config.host}: ')
        connection_string = make_oracle_connection_string(
            user,
            password,
            config.host,
            config.service_name
        )

    return create_engine(connection_string, max_identifier_length=128, connect_args={"encoding": "ISO-8859-1"})


def create_psycopg2_connection(database_config_file='pgdb_config.json'):

    # read the config
    config = PostgreDatabaseConfig(database_config_file)

    # generate connection string
    if 'user' in config and 'password' in config:
        connection_string = "dbname='{0}' user='{1}' host='{2}' password='{3}'".format(config.db_name, config.user, config.host, config.password)
    else:
        # lets ask the user for his database password
        user = os.getlogin()
        password = getpass(f'Database Password for {user} on {config.host}: ')
        connection_string = "dbname='{0}' user='{1}' host='{2}' password='{3}'".format(config.db_name, user, config.host, password)

    return psycopg2.connect(connection_string)


def create_oracle_connection(database_config_file='db_config_idsds.json'):

    config = OracleDatabaseConfig(database_config_file)
    dsn = cx.makedsn(config.host, 1521, service_name=config.service_name)
    # generate connection string
    if 'user' in config and 'password' in config:
        connection = cx.connect(config.user, config.password, dsn, encoding="UTF-8")
    else:
        # lets ask the user for his database password
        user = os.getlogin()
        password = getpass(f'Database Password for {user} on {config.host}: ')
        connection = cx.connect(user, password, dsn, encoding="UTF-8")

    return connection
    

def create_postgre_engine(database_config_file='pgdb_config.json'):

    # read the config
    config = PostgreDatabaseConfig(database_config_file)

    return create_engine("postgresql://{0}:{1}@{2}:5432/{3}".format(
                config.user, config.password, config.host, config.db_name), connect_args={'sslmode': 'require'})


def make_oracle_connection_string(user, pw, host, service_name):

    dns_str = cx.makedsn(host, '1521', service_name)

    # replace SID with SERVICE_NAME
    dns_str = dns_str.replace('SID', 'SERVICE_NAME')

    connection_string = 'oracle+cx_oracle://{0}:{1}@{2}'.format(
        user,
        pw,
        dns_str
    )

    return connection_string
