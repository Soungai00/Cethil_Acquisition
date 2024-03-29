Keithley 2700 Multimeter
========================

This section focus on the Pymodaq keithley2700 plugin which is designed to interact with a Keithley 2700 Multimeter/Switch System.
It enables you to remotly control the instrument and acquire data (e.g. voltages,temperatures..)

*******************
Plugin installation
*******************

The pymodaq_plugin_keithley2700 package is available `here`_:

.. _here: https://git-cethil.insa-lyon.fr/instrumentation/Cethil-Acquisition/-/tree/master/Keithley2700/pymodaq_plugins_keithley2700?ref_type=heads

Once downloaded, extract the package in the local repository you want, and install it::

    $ pip install pymodaq_plugin_keithley2700
    $ pip install pyvisa

.. note::
    The plugin requires the python package pyvisa.

******************
Instrument control
******************

- Hardware
    - Connect the Keithley power supply cable
    - Connect the Keithley to the PC (RS232 connexion is the only one supported at this point, later will be implemented GPIB/TCIP)
    - Power on the Keithley

- Software
    - Launch Pymodaq dashboard running (in your dedicated environmnent) the command::

        $ dashboard

    This window should open (if not, please check carefully the previous installation procedure, you may have installed the wrong version or miss a necessary package):

    .. image:: ../images/pymodaq_dashboard.PNG
        :width: 1000

    - Load existing preset, if not, you can create a new one as shown below:

    .. image:: ../images/pymodaq_newpreset.PNG
        :width: 1000

	    - No actuator
	    - 1 Detector (0D for sample visualization, 1D for temporal plots but not fully implemented)

        .. image:: ../images/pymodaq_newpreset_det00_keithley.PNG
            :width: 1000

    - The daq_viewer window open automaticaly when loading preset. Instead of using the dashboard, you can run it directly through your prompt running::

        $ daq_viewer

