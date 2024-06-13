# -*- coding: utf-8 -*-
"""
Created the 31/08/2023

@author: Sebastien Weber
"""
import os
from pathlib import Path
from pymodaq.utils.config import BaseConfig, USER

class Config(BaseConfig):
    """Main class to deal with configuration values for this plugin"""
    config_template_path = Path(__file__).parent.joinpath(f"resources/config_{__package__.split('pymodaq_plugins_')[1]}.toml")
    config_name = f"config_{__package__.split('pymodaq_plugins_')[1]}"

toml_modules = [f for f in os.listdir('resources/') if "module" in f and ".toml" in f]
print("--- Modules conf files:",toml_modules)

for file in toml_modules:
    class ConfigModule(BaseConfig):
        config_template_path = Path(__file__).parent.joinpath("resources/config_module" + str(file[-9:-5]) + ".toml")
        config_name = f"config_module" + str(file[-9:-5])

    exec("class Config_k" + str(file[-9:-5]) + "(ConfigModule): pass")