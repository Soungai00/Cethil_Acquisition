========================
Developper documentation
========================

This documentation targets users who needs to enter deeper in the code to custom the plugin.

To install a plugin in developper mode, run::

    $ cd <plugin_path>
    $ pip install -e .

It enables you to directly apply your code modification and make pymodaq use your plugin as if it were installed in your environment dependencies.

To include your modifications in the documentation, you will need to install sphinx::

    $ conda install sphinx
    $ pip install sphinx_rtd_theme