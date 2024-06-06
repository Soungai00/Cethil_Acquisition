# -*- coding: utf-8 -*-
"""
Created the 31/08/2023

@author: Sebastien Weber
"""
from pathlib import Path

from pymodaq.utils.config import BaseConfig, USER


class Config_k2700(BaseConfig):
    """Main class to deal with configuration values for this plugin"""
    config_template_path = Path(__file__).parent.joinpath('resources/config_k2700_module7706.toml')
    config_name = f"config_k2700_module7706"

class Config_k2701(BaseConfig):
    """Main class to deal with configuration values for this plugin"""
    config_template_path = Path(__file__).parent.joinpath('resources/config_k2701_module7708.toml')
    config_name = f"config_k2701_module7708"