# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

import os
import sys
# sys.path.insert(0, os.path.abspath('..')) #No need while only documenting Keithley2700
sys.path.insert(0, os.path.abspath('..\Keithley2700\pymodaq_plugins_keithley2700\src'))
sys.path.insert(0, os.path.abspath('..\.conda\PmDev\Lib\site-packages'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Cethil Acquisition'
copyright = '2024, Sébastien Guerrero'
author = 'Sébastien Guerrero'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.todo",
              "sphinx.ext.viewcode",
              "sphinx.ext.autodoc", # Core library for html generation from docstrings
              "sphinx.ext.graphviz",
              "sphinx.ext.inheritance_diagram"
              ]

autodoc_default_flags = ['members', 'inherited-members', 'show-inheritance']
autodoc_default_options = {
    "members": True,
    "special-members": "__init__",
    "inherited-members": False,
    "show-inheritance": False,
}

inheritance_graph_attrs = dict(rankdir="TB", size='""')

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']