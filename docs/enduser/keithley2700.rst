Pymodaq plugin: keithley2700
============================

This plugin is designed to interact with a Keithley 2700 Multimeter/Switch System.
It enables you to remotly control your instrument and acquire data (e.g. voltages,temperatures..)

*******************
Plugin installation
*******************

To install a custom plugin, you need to pip install it in your environment directory::

    $ cd C:\Users\[...]\Pymodaq_ENV_NAME
    $ pip install PLUGIN_NAME (type: pymodaq_plugin_device)

So for the Keithley2700::

    $ pip install pymodaq_plugin_keithley2700
    $ pip install pyvisa		#Needed for Keithley2700 plugin


******************
Instrument control
******************

- Connect the Keithley power supply cable
- Connect the Keithley to the PC (RS232 connexion)
- Power on the Keithley

- Launch Pymodaq dashboard running (in your dedicated environmnent) the command::

    $ dashboard

- Load existing preset, if not, you can create a new one:
	- No actuator
	- 1 Detector (0D for sample visualization, 1D for temporal plots but not fully implemented)

- The daq_viewer window open automaticaly when loading preset. Instead of using the dashboard, you can run it directly through your prompt running::

    $ daq_viewer

