import configparser
import os
from .constants import config_names, ConfigOptions


class ConfigNotFoundError(Exception):
    pass


def get_wrapper(file: str):

    cfg = configparser.ConfigParser()
    cfg.read(file)

    def get(option: ConfigOptions):
        # always prio env variable over ini settings
        option_val: str = os.environ.get(
            config_names[option]['env'])

        if option_val is None:
            if config_names[option]['settings'] in cfg['Default']:
                option_val = cfg['Default'][config_names[option]['settings']]
            else:
                raise ConfigNotFoundError(
                    f"Config {option} neither configured in settings.ini nor as env variable.")

        return option_val

    return get
