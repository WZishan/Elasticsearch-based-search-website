from enum import Enum


class ConfigOptions(Enum):
    URL = 1
    USERNAME = 2
    PASSWORD = 3


config_names = {
    ConfigOptions.URL: {
        "env": "ELASTICSEARCH_URL",
        "settings": "URL"
    },
    ConfigOptions.PASSWORD: {
        "env": "ELASTICSEARCH_PASSWORD",
        "settings": "PASSWORD"
    },
    ConfigOptions.USERNAME: {
        "env": "ELASTICSEARCH_USERNAME",
        "settings": "USERNAME"
    }
}
