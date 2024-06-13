import os
from pathlib import Path
from pymodaq.utils.logger import set_logger  # to be imported by other modules.

import pymodaq_plugins_keithley.utils as utils

config_keithley = utils.Config()
toml_modules = [f for f in os.listdir('resources/') if "module" in f and ".toml" in f]
for file in toml_modules:
    exec("config_k" + str(file[-9:-5]) + " = " + "utils.Config_k" + str(file[-9:-5]) + "()")

with open(str(Path(__file__).parent.joinpath('resources/VERSION')), 'r') as fvers:
    __version__ = fvers.read().strip()