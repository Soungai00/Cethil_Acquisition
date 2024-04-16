Pymodaq installation
====================

Before installing pymodaq, check if anaconda3 is installed on your PC. 
If not, you can download it here:
https://www.anaconda.com/

.. note::
    It is not mandatory to use anaconda but for convenience (and comfort) reason, it is strongly recommanded.
    Moreover, all the tests have been made in a virtual anaconda environment.

In the same way, it is recommended to create a dedicated environment to install Pymodaq and work with.

To do so, either open an Anaconda3 prompt directly or open a command prompt and run::

    $ C:\Anaconda3\condabin\activate.bat

Then, run the following sequence::

	$ conda create --name Pymodaq_ENV_NAME python=3.8
	$ conda deactivate
	$ conda activate Pymodaq_ENV_NAME
	$ conda install pyqt
	$ pip install pymodaq==4.0.11

.. note::
    To install specific version, run::
        
        $ conda install package_name=version
        $ pip install package_name==version

    Python 3.8 and Pymodaq 4.0.11 are the ones used during the tests.

.. warning::
    Pymodaq requires the python package pyqt, don't forget it !

Once Pymodaq installed, you will now need to install plugins according to the instrument you use.
You can find the list of all available plugins running the plugin manager::
    $ plugin_manager

Or check it on https://github.com/PyMoDAQ/pymodaq_plugin_manager.
If you want to use a custom plugin, you need to pip install it in your working environment::

    $ cd <PATH_TO_YOUR_ENV>\Pymodaq_ENV_NAME
    $ pip install PLUGIN_NAME (type: pymodaq_plugin_device)
