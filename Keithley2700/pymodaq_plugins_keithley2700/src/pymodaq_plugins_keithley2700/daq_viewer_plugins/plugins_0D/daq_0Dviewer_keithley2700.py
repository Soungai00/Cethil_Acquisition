import time
import numpy as np
from easydict import EasyDict as edict
from pymodaq.utils.daq_utils import ThreadCommand
from pymodaq.utils.data import DataFromPlugins, DataToExport
from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.utils.parameter import Parameter
from ...hardware.keithley2700_VISADriver import Keithley2700VISADriver as Keithley2700
import configparser

# Read configuration file
config = configparser.ConfigParser()
config.read('k2700config.ini')
rsrc_name = config['INSTRUMENT']['rsrc_name']
panel = config['INSTRUMENT']['panel'].upper()
channels = config['PARAMETERS']['chan_to_read']

Chan_to_plot=[]
for i in range(len(channels.split(','))):
    Chan_to_plot.append('Channel '+str(channels.split(',')[i]))

class DAQ_0DViewer_Keithley2700(DAQ_Viewer_base):
    """ Keithley 2700 plugin class for a OD viewer.
    
    This object inherits all functionalities to communicate with PyMoDAQ’s DAQ_Viewer module through inheritance via
    DAQ_Viewer_base. It makes a bridge between the DAQ_Viewer module and the Python wrapper of a the keithley 2700.

    TODO Complete the docstring of your plugin with:
        * The set of instruments that should be compatible with this instrument plugin.
        * With which instrument it has actually been tested.
        * The version of PyMoDAQ during the test.
        * The version of the operating system.
        * Installation instructions: what manufacturer’s drivers should be installed to make it run?

    Attributes:
    -----------
    controller: object
        The particular object that allow the communication with the hardware, in general a python wrapper around the
         hardware library.
    params: dictionnary list
    x_axis: 1D numpy array
    ind_data: int
    
    """
    # params = comon_parameters+[
    #     {'title': 'Keithley2700',  'name': 'K2700Params', 'type': 'group', 'children': [
    #         {'title': 'Fonctionnement', 'name': 'K2700Fonct', 'type': 'group', 'children': [
    #             {'title': 'FRONT panel', 'name': 'frontpanel', 'type': 'group', 'children': [
    #                 {'title': 'Mode', 'name': 'frontmode', 'type': 'list', 'limits': ['VDC','VAC','IDC','IAC','R2W','R4W','FREQ','TEMP'], 'value': 'VDC'}]},
    #             {'title': 'REAR panel', 'name': 'rearpanel', 'type': 'group', 'children': [
    #                 {'title': 'Mode', 'name': 'rearmode', 'type': 'list', 'limits': ['SCAN_VDC', 'SCAN_VAC', 'SCAN_IDC', 'SCAN_IAC', 'SCAN_R2W', 'SCAN_R4W', 'SCAN_FREQ', 'SCAN_TEMP'], 'value': 'SCAN_VDC'}
    #             ]}
    #         ]}
    #     ]}
    #     ]

    if panel == 'FRONT':
        print('Panel configuration :',panel)
        params = comon_parameters+[
            {'title': 'Keithley2700',  'name': 'K2700Params', 'type': 'group', 'children': [
                {'title': 'FRONT panel', 'name': 'frontpanel', 'type': 'group', 'children': [
                    {'title': 'Mode', 'name': 'frontmode', 'type': 'list', 'limits': ['VDC','VAC','IDC','IAC','R2W','R4W','FREQ','TEMP'], 'value': 'VDC'}]}
            ]}
        ]
    elif panel == 'REAR':
        print('Panel configuration :',panel)
        params = comon_parameters+[
            {'title': 'Keithley2700',  'name': 'K2700Params', 'type': 'group', 'children': [
                {'title': 'REAR panel', 'name': 'rearpanel', 'type': 'group', 'children': [
                    {'title': 'Mode', 'name': 'rearmode', 'type': 'list', 'limits': ['VDC', 'VAC', 'IDC', 'IAC', 'R2W', 'R4W', 'FREQ', 'TEMP'], 'value': 'VDC'}
                ]}
            ]}
        ]

    def __init__(self, parent=None, params_state=None):
        super(DAQ_0DViewer_Keithley2700, self).__init__(parent, params_state)
        self.x_axis = None
        self.ind_data = 0

    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        if 'mode' in param.name():
            """Updates the newly selected measurement mode"""
            print('Parameter :',param.value())
            # Read the configuration file to determine which mode to use
            if panel == 'FRONT':
                value = param.value()
                self.controller.set_mode(value)
            elif panel == 'REAR':
                value = 'SCAN_'+param.value()
                self.controller.set_mode(value)
            print('Cmd sent to driver :',value)

    def ini_detector(self, controller=None):
        """Detector communication initialization

        Parameters
        ----------
        controller: (object)
            custom object of a PyMoDAQ plugin (Slave case). None if only one actuator/detector by controller
            (Master case)

        Returns
        -------
        info: str
        initialized: bool
            False if initialization failed otherwise True
        """

        self.status.update(edict(initialized=False, info="", x_axis=None, y_axis=None, controller=None))
        if self.settings.child(('controller_status')).value() == "Slave":
            if controller is None: 
                raise Exception('no controller has been defined externally while this detector is a slave one')
            else:
                self.controller = controller
        else:
            try:
                self.controller = Keithley2700(rsrc_name)
            except Exception as e:
                raise Exception('No controller could be defined because an error occurred\
                 while connecting to the instrument. Error: {}'.format(str(e)))
        
        # Reset Keithley
        self.controller.reset()
        # Initilize detector communication and set the default value (VDC)
        if panel == 'FRONT':
            value = self.settings.child('K2700Params', 'frontpanel', 'frontmode').value()
            self.controller.set_mode(value)
        elif panel == 'REAR':
            value = 'SCAN_'+self.settings.child('K2700Params', 'rearpanel', 'rearmode').value()
            self.controller.set_mode(value)

        # Initialize viewers with the future type of data
        self.data_grabed_signal.emit([DataFromPlugins(name='Keithley2700', data=[np.array([0])], dim='Data0D', labels=['Meas', 'Time'])])

        self.status.initialized = True
        self.status.controller = self.controller
        
        return self.status

    def close(self):
        """Terminate the communication protocol"""
        ## TODO for your custom plugin
        #  self.controller.your_method_to_terminate_the_communication()  # when writing your own plugin replace this line
        pass

    def grab_data(self, Naverage=1, **kwargs):
        """Start a grab from the detector

        Parameters
        ----------
        Naverage: int
            Number of hardware averaging (if hardware averaging is possible, self.hardware_averaging should be set to
            True in class preamble and you should code this implementation)
        kwargs: dict
            others optionals arguments
        """
        ## TODO for your custom plugin: you should choose EITHER the synchrone or the asynchrone version following

        # synchrone version (blocking function)
        # self.dte_signal.emit(DataToExport(name='keithley2700',
        #                                   data=[DataFromPlugins(name=rsrc_name, data=data_tot,
        #                                                         dim='Data0D', labels=['dat0', 'data1'])]))

        # Read data
        if panel == 'FRONT':
            data_tot = self.controller.read()[1]
            print(data_tot)
        elif panel == 'REAR':
            print(Chan_to_plot)
            data_tot = self.controller.read()[1]
            print(data_tot)
            for i in range(len(Chan_to_plot)):
                print(Chan_to_plot[i]+': ',data_tot[i])
        
        # Grab the 1st data of each scan array
        self.data_grabed_signal.emit([DataFromPlugins(name=rsrc_name,
                                                      data=[np.array([data_tot[i]]) for i in range(len(data_tot))],
                                                      dim='Data0D',
                                                      labels=[Chan_to_plot[i] for i in range(len(Chan_to_plot))])])

        # self.data_grabed_signal.emit([DataFromPlugins(name=rsrc_name, data=[data_tot], dim='Data0D', labels=['dat0', 'data1'])])

        #########################################################

        # asynchrone version (non-blocking function with callback)
        # raise NotImplemented  # when writing your own plugin remove this line
        # self.controller.your_method_to_start_a_grab_snap(self.callback)  # when writing your own plugin replace this line
        #########################################################


    # def callback(self):
        # """optional asynchrone method called when the detector has finished its acquisition of data"""
        # data_tot = self.controller.your_method_to_get_data_from_buffer()
        # self.dte_signal.emit(DataToExport(name='myplugin',
                                        #   data=[DataFromPlugins(name='Mock1', data=data_tot,
                                                                # dim='Data0D', labels=['dat0', 'data1'])]))

    def stop(self):
        """Stop the current grab hardware wise if necessary"""
        self.controller.stop_acquisition()
        self.emit_status(ThreadCommand('Update_Status', ['Acquisition stoped']))
        return ''


if __name__ == '__main__':
    main(__file__)
