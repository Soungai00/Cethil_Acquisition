from pathlib import Path
from pymodaq.utils.logger import set_logger  # to be imported by other modules.

from pymodaq_plugins_keithley2700.utils import Config
config = Config()

with open(str(Path(__file__).parent.joinpath('resources/VERSION')), 'r') as fvers:
    __version__ = fvers.read().strip()
