import os

from .config_manager import get_wrapper
from .constants import ConfigOptions as Config # noqa

__location__ = os.path.normpath(os.path.join(os.path.dirname(__file__), "../.."))

files_ext = f"{__location__}/settings.ini"
get = get_wrapper(file=files_ext)
