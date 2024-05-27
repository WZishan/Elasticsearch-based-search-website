import json
import os
from pathlib import Path


def get_full_path(relative_path, relative_to_project_root=True):
    """Returns the absolute path of a relative file path.

    All relative file paths in the project are with respect
    to the root directory of the sandbox project. In python
    relative file imports are, by default, relative to the
    directory from which python gets executed, resulting in
    the config files not being found. This funciton returns
    the absolute path of a relative path with respect to the
    project root directory.

    Parameters
    ----------
    relative_path: string
        relative path with respect to the root project directory
        or relative to the current working directory.

    relative_to_project_root: boolean
        If True, the relative path is interpreted relative to the
        root project directory. If False, the relative path is
        interpreted relative to the current working directory.

    Returns
    -------
    string
        absolute path of the specified relative path.
    """

    if relative_to_project_root:
        root_dir = Path(__file__).parent.parent.parent.resolve()
    else:
        root_dir = Path.cwd()
    return os.path.join(root_dir, relative_path)


class ConfigError(Exception):
    pass


class BaseConfig:

    def __init__(self, required_keys, config_file_path):

        # if required_keys is a list and not a set, we convert it
        if isinstance(required_keys, list):
            self.required_keys = set(required_keys)
        elif isinstance(required_keys, set):
            self.required_keys = required_keys
        else:
            # required_keys is neither a list nor a set
            raise ValueError('Required_keys needs to be a list or a set!')

        with open(get_full_path(
                config_file_path, relative_to_project_root=False)) as jfile:
            data = json.load(jfile)

        if self.required_keys.issubset(data.keys()) is False:
            raise ConfigError('Not all required keys specified in '
                              'the config file. Required keys are '
                              f'{self.required_keys}.')
        else:
            self.data = data

    def __getattr__(self, item):
        return self.data[item]

    def __contains__(self, item):
        return item in self.data


class OracleDatabaseConfig(BaseConfig):

    __required_keys = {'host', 'service_name', 'schema'}

    def __init__(self, config_file_path):
        super().__init__(self.__required_keys, config_file_path)

class PostgreDatabaseConfig(BaseConfig):

    __required_keys = {'host', 'db_name'}

    def __init__(self, config_file_path):
        super().__init__(self.__required_keys, config_file_path)