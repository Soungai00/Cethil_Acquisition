Pymodaq installation
====================

Before installing pymodaq, check if anaconda3 is installed on your PC. 
If not, you can download it here:
https://www.anaconda.com/

.. note::
    It is not mandatory to use anaconda but for convenience (and comfort) reason, it is strongly recommanded.
    Moreover, all the tests have been made in a virtual anaconda environment.

In the same way, it is recommended to create a dedicated environment to install Pymodaq and work with.

To do so, open a command prompt & run the following sequence (By opening an Anaconda3 prompt directly, skip the first line)::

    $ C:\Anaconda3\condabin\activate.bat
	$ conda create --name Pymodaq_ENV_NAME python=3.12.0
	$ conda deactivate
	$ conda activate Pymodaq_ENV_NAME
	$ conda install pyqt
	$ pip install pymodaq==4.0.11

.. note::
    To install specific version, run::
        
        $ conda install package_name=version
        $ pip install package_name==version

    Pymodaq 4.0.11 and python 3.12.0, used during the tests, work well.


