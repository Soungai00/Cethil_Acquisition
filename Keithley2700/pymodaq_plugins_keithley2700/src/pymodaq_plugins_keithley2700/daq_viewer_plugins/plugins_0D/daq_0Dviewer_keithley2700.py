import os
import numpy as np
from easydict import EasyDict as edict
from pymodaq.utils.daq_utils import ThreadCommand
from pymodaq.utils.data import DataFromPlugins, DataToExport
from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.utils.parameter import Parameter

from pymodaq_plugins_keithley2700 import config as k2700config
from ...hardware.keithley2700_VISADriver import Keithley2700VISADriver as Keithley2700

class DAQ_0DViewer_Keithley2700(DAQ_Viewer_base):
    """ Keithley 2700 plugin class for a OD viewer.
    
    This object inherits all functionalities to communicate with PyMoDAQ’s DAQ_Viewer module through inheritance via
    DAQ_Viewer_base. It makes a bridge between the DAQ_Viewer module and the Python wrapper of a the keithley 2700.

    * Keithley 27XX should be compatible with this plugin
    * Tested with Keithley 2700 Multimeter/Switch System
    * PyMoDAQ version = 4.0.11 during the test

    Attributes:
    -----------
    controller: object
        The particular object that allow the communication with the hardware, in general a python wrapper around the hardware library.
    params: dictionnary list
    x_axis: 1D numpy array
    mode: str
    
    """
    # Read configuration file
    rsrc_name = k2700config('INSTRUMENT').get('rsrc_name')
    panel = k2700config('INSTRUMENT').get('panel').upper()
    channels = k2700config('CHANNELS').keys()

    if panel == 'FRONT':
        print('Panel configuration 0D viewer:',panel)
        params = comon_parameters+[
            {'title': 'Keithley2700',  'name': 'K2700Params', 'type': 'group', 'children': [
                {'title': 'FRONT panel', 'name': 'frontpanel', 'type': 'group', 'children': [
                    {'title': 'Mode', 'name': 'frontmode', 'type': 'list', 'limits': ['VDC','VAC','IDC','IAC','R2W','R4W','FREQ','TEMP'], 'value': 'VDC'}]}
            ]}
        ]
    elif panel == 'REAR':
        print('Panel configuration 0D viewer:',panel)
        params = comon_parameters+[
            {'title': 'Keithley2700',  'name': 'K2700Params', 'type': 'group', 'children': [
                {'title': 'REAR panel', 'name': 'rearpanel', 'type': 'group', 'children': [
                    {'title': 'Mode', 'name': 'rearmode', 'type': 'list', 'limits': ['SCAN_LIST','VDC', 'VAC', 'IDC', 'IAC', 'R2W', 'R4W', 'FREQ', 'TEMP'], 'value': 'SCAN_LIST'}
                ]}
            ]}
        ]

    # Remove current measurement from parameters when non-amps modules
    if Keithley2700(rsrc_name).non_amp_module == True:
        params[1]['children'][0]['children'][0]['limits'] = [i for i in params[1]['children'][0]['children'][0]['limits'] if not 'IAC' in i and not 'IDC' in i]

    def __init__(self, parent=None, params_state=None):
        super(DAQ_0DViewer_Keithley2700, self).__init__(parent, params_state)
        self.x_axis = None
        self.channels_in_selected_mode = None
        self.params_cacahuete = None

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
            if DAQ_0DViewer_Keithley2700.panel == 'FRONT':
                value = param.value()
                self.controller.set_mode(value)
            elif DAQ_0DViewer_Keithley2700.panel == 'REAR':
                value = 'SCAN_'+param.value()
                self.channels_in_selected_mode = self.controller.set_mode(value)
                print('Channels to plot :',self.channels_in_selected_mode)

            print('DAQ_viewer command sent to keithley visa driver :',value)

    def ini_detector(self, controller=None):
        """Detector communication initialization

        :param controller: Custom object of a PyMoDAQ plugin (Slave case). None if only one actuator/detector by controller (Master case)
        :type controller: object

        Returns
        -------
        info: str
        initialized: bool
            False if initialization failed otherwise True
        """
        print('Detector 0D initialized')
        
        self.status.update(edict(initialized=False, info="", x_axis=None, y_axis=None, controller=None))
        if self.settings.child(('controller_status')).value() == "Slave":
            if controller is None: 
                raise Exception('no controller has been defined externally while this detector is a slave one')
            else:
                self.controller = controller
        else:
            try:
                self.controller = Keithley2700(DAQ_0DViewer_Keithley2700.rsrc_name)
            except Exception as e:
                raise Exception('No controller could be defined because an error occurred\
                 while connecting to the instrument. Error: {}'.format(str(e)))
        
        # Reset Keithley
        self.controller.configuration_sequence()
        # Initilize detector communication and set the default value (VDC)
        if DAQ_0DViewer_Keithley2700.panel == 'FRONT':
            value = self.settings.child('K2700Params', 'frontpanel', 'frontmode').value()
            self.controller.set_mode(value)
        elif DAQ_0DViewer_Keithley2700.panel == 'REAR':
            value = 'SCAN_'+self.settings.child('K2700Params', 'rearpanel', 'rearmode').value()
            self.channels_in_selected_mode = self.controller.set_mode(value)
            print('Channels to plot :',self.channels_in_selected_mode)
        print('DAQ_viewer command sent to keithley visa driver :',value)

        # Initialize viewers with the future type of data
        self.dte_signal.emit(DataToExport(name='keithley2700',
                                          data=[DataFromPlugins(name=DAQ_0DViewer_Keithley2700.rsrc_name,
                                                                data=[np.array([0])],
                                                                dim='Data0D',
                                                                labels=['Meas', 'Time'])]))

        self.status.initialized = True
        self.status.controller = self.controller
        
        return self.status

    def close(self):
        """Terminate the communication protocol"""
        self.controller.reset()
        print('communication ended successfully')

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
        channels_in_selected_mode = self.channels_in_selected_mode[1:-1].replace('@','')
        # Read data_tot
        if DAQ_0DViewer_Keithley2700.panel == 'FRONT':
            data_tot = self.controller.data()[1]
            print('Data tot :',data_tot)
        elif DAQ_0DViewer_Keithley2700.panel == 'REAR':
            Chan_to_plot=[]
            for i in range(len(channels_in_selected_mode.split(','))):
                Chan_to_plot.append('Channel '+str(channels_in_selected_mode.split(',')[i]))
            print(Chan_to_plot)
            data_tot = self.controller.data()[1]
            print('Data :',data_tot)

        # When reading the scan_list, data are displayed and exported grouped by mode
        if self.controller.reading_scan_list == False:

            # Grab data
            data = DataToExport(name='keithley2700',
                                            data=[DataFromPlugins(name='Temperatures',
                                                                    data=[np.array([data_tot[i]]) for i in range(len(data_tot))],
                                                                    dim='Data0D',
                                                                    labels=[Chan_to_plot[i] for i in range(len(Chan_to_plot))])
                                                    ])
        
        elif self.controller.reading_scan_list == True:
            print('modes channel dict : ', self.controller.modes_channels_dict)

            # Grab data
            data = DataToExport(name='keithley2700',
                                            data=[DataFromPlugins(name='Temperatures',
                                                                    data=[np.array([data_tot[0]]), np.array([data_tot[1]])],
                                                                    dim='Data0D',
                                                                    labels=[Chan_to_plot[0], Chan_to_plot[1]]),
                                                    DataFromPlugins(name='Voltage',
                                                                    data=[np.array([data_tot[3]])],
                                                                    dim='Data0D',
                                                                    labels=[Chan_to_plot[3]]),
                                                    DataFromPlugins(name='Resistance',
                                                                    data=[np.array([data_tot[2]])],
                                                                    dim='Data0D',
                                                                    labels=[Chan_to_plot[2]])
                                                    ])
        
        self.dte_signal.emit(data)
        
        # Write data in txt file
        if not os.path.exists('Keithley2700_data_det0D.txt'):
            open('Keithley2700_data_det0D.txt','w')
        file = open('Keithley2700_data_det0D.txt','a')
        for i in range(len(data_tot)):
            file.write(str(data_tot[i])+' ')
        file.write('\n')


        # Export data to database



    def stop(self):
        """Stop the current grab hardware wise if necessary"""
        self.emit_status(ThreadCommand('Update_Status', ['Acquisition stoped']))
        return ''

if __name__ == '__main__':
    main(__file__)