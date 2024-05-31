from pathlib import Path
from pymodaq.utils.logger import set_logger  # to be imported by other modules.

from pymodaq_plugins_keithley.utils import Config_k2700, Config_k2701
config_k2700 = Config_k2700()
config_k2701 = Config_k2701()

with open(str(Path(__file__).parent.joinpath('resources/VERSION')), 'r') as fvers:
    __version__ = fvers.read().strip()

