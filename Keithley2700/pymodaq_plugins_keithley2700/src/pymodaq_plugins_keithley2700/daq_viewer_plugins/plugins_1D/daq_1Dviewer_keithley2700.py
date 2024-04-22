import time
import datetime
import numpy as np
from easydict import EasyDict as edict
from pymodaq.utils.daq_utils import ThreadCommand
from pyqtgraph.dockarea import Dock, DockArea
from pymodaq.utils.data import Axis, DataFromPlugins, DataToExport
from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.utils.parameter import Parameter, ParameterTree

from pymodaq_plugins_keithley2700 import config as k2700config
from ...hardware.keithley2700_VISADriver import Keithley2700VISADriver as Keithley2700

class DAQ_1DViewer_Keithley2700(DAQ_Viewer_base):
    """ Keithley 2700 plugin class for a OD viewer.
    
    This object inherits all functionalities to communicate with PyMoDAQ’s DAQ_Viewer module through inheritance via
    DAQ_Viewer_base. It makes a bridge between the DAQ_Viewer module and the Python wrapper of a the keithley 2700.

    * Keithley 27XX should be compatible with this plugin
    * Tested with Keithley 2700 Multimeter/Switch System
    * PyMoDAQ version = 4.0.11 during the test

    :param controller: The particular object that allow the communication with the hardware, in general a python wrapper around the hardware library.
    :type  controller:  object

    :param params:
    :type params: dictionnary list

    :param x_axis: Daq_1Dviewer data are acquired as a function of time
    :type x_axis: 1D numpy array

    :param start_time:
    :type start_time: Nonetype
    """

    # Read configuration file
    rsrc_name = k2700config('INSTRUMENT').get('rsrc_name')
    panel = k2700config('INSTRUMENT').get('panel').upper()
    channels = k2700config('CHANNELS').keys()

    if panel == 'FRONT':
        print('Panel configuration 1D viewer:',panel)
        params = comon_parameters+[
            {'title': 'Keithley2700',  'name': 'K2700Params', 'type': 'group', 'children': [
                {'title': 'ID', 'name': 'ID', 'type': 'text', 'value': ''},
                {'title': 'FRONT panel', 'name': 'frontpanel', 'type': 'group', 'children': [
                    {'title': 'Mode', 'name': 'frontmode', 'type': 'list', 'limits': ['VOLT:DC','VOLT:AC','CURR:DC','CURR:AC','RES','FRES','FREQ','TEMP'], 'value': 'VOLT:DC'}]}
            ]}
        ]
    elif panel == 'REAR':
        print('Panel configuration 1D viewer:',panel)
        params = comon_parameters+[
            {'title': 'Keithley2700',  'name': 'K2700Params', 'type': 'group', 'children': [
                {'title': 'ID', 'name': 'ID', 'type': 'text', 'value': ''},
                {'title': 'REAR panel', 'name': 'rearpanel', 'type': 'group', 'children': [
                    {'title': 'Mode', 'name': 'rearmode', 'type': 'list', 'visible':True, 'limits': ['SCAN_LIST','VOLT:DC','VOLT:AC','CURR:DC','CURR:AC','RES','FRES','FREQ','TEMP'], 'value': 'SCAN_LIST'}
                ]}
            ]}
        ]

    # Remove current measurement from parameters when non-amps modules
    if Keithley2700(rsrc_name).non_amp_module == True:
        params[1]['children'][1]['children'][0]['limits'] = [i for i in params[1]['children'][1]['children'][0]['limits'] if not 'CURR:AC' in i and not 'CURR:DC' in i]

    def __init__(self, parent=None, params_state=None):
        super(DAQ_1DViewer_Keithley2700, self).__init__(parent, params_state)
        self.ini_attributes()

    def ini_attributes(self):
        """Attributes init when DAQ_0DViewer_Keithley2700 class is instancied"""
        self.x_axis = None
        self.channels_in_selected_mode = None
        self.start_time = None

    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        :param Parameter: A given parameter (within detector_settings) whose value has been changed by the user
        """
        if 'mode' in param.name():
            """Updates the newly selected measurement mode"""
            # Read the configuration file to determine which mode to use
            if DAQ_1DViewer_Keithley2700.panel == 'FRONT':
                value = param.value()
                self.controller.set_mode(value)
            elif DAQ_1DViewer_Keithley2700.panel == 'REAR':
                value = 'SCAN_'+param.value()
                self.channels_in_selected_mode = self.controller.set_mode(value)
                if 'TEMP' in param.value():
                    self.Treestate = self.settings.saveState()
                    self.added_dict = {'title': 'TITLE', 'name': 'NAME', 'type': 'list', 'visible':True, 'removable':True, 'syncExpanded':True, 'limits': ['plop','plip']}
                    self.settings.child('K2700Params', 'rearpanel').addChild(self.added_dict, autoIncrementName=None)
                    print('\n ********** Adding child')
                    print('child name : ',self.settings.child('K2700Params', 'rearpanel').child('NAME'))
                    print('self.names :', self.settings.child('K2700Params', 'rearpanel').names)
                    print('self.params : ', self.params)
                    print('self.params type : ',type(self.params))
                    print('self.settings : ', self.settings)
                    print('self.settings type : ',type(self.settings))
                    print('self.settings childs : ',self.settings.childs)
                    print('self.settings.child(K2700params, rearpanel).childs : ',self.settings.child("K2700Params", "rearpanel").childs)

                if 'VOLT:DC' in param.value():
                    print('\n********** Removing child')
                    print('child name : ',self.settings.child('K2700Params', 'rearpanel').child('NAME'))
                    # self.settings.child('K2700Params', 'rearpanel').removeChild(self.settings.child('K2700Params', 'rearpanel').child('NAME'))

                    """Remove a child parameter."""
                    child = self.settings.child('K2700Params', 'rearpanel').child('NAME')
                    name = child.name()
                    if name not in self.settings.child('K2700Params', 'rearpanel').names or self.settings.child('K2700Params', 'rearpanel').names[name] is not child:
                        raise Exception("Parameter %s is not my child; can't remove." % str(child))
                    del self.settings.child('K2700Params', 'rearpanel').names[name]
                    self.settings.child('K2700Params', 'rearpanel').childs.pop(self.settings.child('K2700Params', 'rearpanel').childs.index(child))
                    child.parentChanged(None)
                    try:
                        child.sigTreeStateChanged.disconnect(self.settings.child('K2700Params', 'rearpanel').treeStateChanged)
                    except (TypeError, RuntimeError):  ## already disconnected
                        pass
                    self.settings.child('K2700Params', 'rearpanel').sigChildRemoved.emit(self.settings.child('K2700Params', 'rearpanel'), child)

                    changes = (self.settings.child('K2700Params', 'rearpanel'),"parent","information")
                    self.settings.sigTreeStateChanged.connect(self.send_param_status(self.settings.child('K2700Params', 'rearpanel'),changes))

                    # self.init_tree = ParameterTree()
                    # self.init_tree.setParameters(self.settings, showTop=False)
                    
                    # # Parameters change test
                    # self.settings.QtCore.Signal("childRemoved")
                    # self.settings.child('K2700Params', 'rearpanel').QtCore.Signal("childRemoved")
                    # self.settings.QtCore.Signal(self.settings.child('K2700Params', 'rearpanel').child('NAME'))

                    # sigChildRemoved
                    self.settings.sigChildRemoved
                    print('1 - Passed')
                    self.settings.sigChildRemoved.connect(self.settings._emitChildRemovedChanged)
                    print('2 - Passed')
                    self.settings.child('K2700Params', 'rearpanel').sigChildRemoved
                    print('3 - Passed')
                    self.settings.child('K2700Params', 'rearpanel').sigChildRemoved.connect(self.settings.child('K2700Params', 'rearpanel')._emitChildRemovedChanged)
                    print('4 - Passed')

                    # # sigRemoved
                    # self.settings.sigRemoved
                    # self.settings.sigRemoved.connect(self.settings._emitRemovedChanged)
                    # self.settings.child('K2700Params', 'rearpanel').sigRemoved()
                    # self.settings.child('K2700Params', 'rearpanel').sigRemoved.connect(self.settings._emitChildRemovedChanged)

                    # # sigTreeStateChanged
                    # self.settings.sigTreeStateChanged()
                    # self.settings.sigTreeStateChanged.connect(self.send_param_status)
                    # self.settings.child('K2700Params', 'rearpanel').sigTreeStateChanged(self.settings.child('K2700Params', 'rearpanel'))
                    # self.settings.child('K2700Params', 'rearpanel').sigTreeStateChanged.connect(self.settings.child('K2700Params', 'rearpanel').send_param_status)

                    print('self.names :', self.settings.child('K2700Params', 'rearpanel').names)
                    print('self.params : ', self.params)
                    print('self.params type : ',type(self.params))
                    print('self.settings : ', self.settings)
                    print('self.settings type : ',type(self.settings))
                    print('self.settings.child(K2700params, rearpanel).childs : ',self.settings.child("K2700Params", "rearpanel").childs)

                    self.settings.restoreState(self.Treestate)

                    # self.settings.clearChildren()

                    # with self.settings.treeChangeBlocker():
                    #     if child.parent() is not None:
                    #         child.remove()
                            
                    #     self.settings.sigTreeStateChanged.connect(self.settings.treeStateChanged)
                    #     self.settings.sigChildAdded.emit(self.settings, child, pos)
                    
    def ini_detector(self, controller=None):
        """Detector communication initialization

        :param controller: Custom object of a PyMoDAQ plugin (Slave case). None if only one actuator/detector by controller (Master case)
        :type controller: object

        :return: Initialization status, false if it failed otherwise True
        :rtype: bool
        """
        print('Detector 1D initialized')

        self.status.update(edict(initialized=False, info="", x_axis=None, y_axis=None, controller=None))
        if self.settings.child(('controller_status')).value() == "Slave":
            if controller is None: 
                raise Exception('no controller has been defined externally while this detector is a slave one')
            else:
                self.controller = controller
        else:
            try:
                self.controller = Keithley2700(DAQ_1DViewer_Keithley2700.rsrc_name)
            except Exception as e:
                raise Exception('No controller could be defined because an error occurred\
                 while connecting to the instrument. Error: {}'.format(str(e)))
        
        # Keithley identification
        txt = self.controller.get_idn()
        self.settings.child('K2700Params','ID').setValue(txt)

        # Initilize detector communication and set the default value (SCAN_LIST)
        if DAQ_1DViewer_Keithley2700.panel == 'FRONT':
            value = self.settings.child('K2700Params', 'frontpanel', 'frontmode').value()
            self.controller.current_mode = value
            self.controller.set_mode(value)
        elif DAQ_1DViewer_Keithley2700.panel == 'REAR':
            self.controller.configuration_sequence()
            value = 'SCAN_'+self.settings.child('K2700Params', 'rearpanel', 'rearmode').value()
            self.channels_in_selected_mode = self.controller.set_mode(value)
            print('Channels to plot :',self.channels_in_selected_mode)
        print('DAQ_viewer command sent to keithley visa driver :',value)
        
        self.status.initialized = True
        self.status.controller = self.controller
        
        return self.status

    def close(self):
        """Terminate the communication protocol"""
        self.controller.close()
        print('communication ended successfully')

    def grab_data(self, Naverage=1, **kwargs):
        """Start a grab from the detector

        :param Naverage: Number of hardware averaging (if hardware averaging is possible, self.hardware_averaging should be set to
            True in class preamble and you should code this implementation)
        :type Naverage: int

        :param kwargs: others optionals arguments
        :type kwargs: dict
        """
        # TIME
        if self.start_time == None:
            self.start_time = time.time()
        grabbed_time = time.time()

        # ACQUISITION OF DATA
        if DAQ_1DViewer_Keithley2700.panel == 'FRONT':
            data_tot = self.controller.data()
            data_measurement = data_tot[1]
            data_time = data_tot[2]
            data_time_univ = data_time + grabbed_time - self.start_time
            print('Data tot :',data_tot)
            print('Data measurement :',data_measurement)
        elif DAQ_1DViewer_Keithley2700.panel == 'REAR':
            print('current mode', self.controller.current_mode)
            channels_in_selected_mode = self.channels_in_selected_mode[1:-1].replace('@','')
            Chan_to_plot=[]
            data_tot = self.controller.data()
            data_measurement = data_tot[1]
            for i in range(len(channels_in_selected_mode.split(','))):
                Chan_to_plot.append('Channel '+str(channels_in_selected_mode.split(',')[i]))
            data_time = data_tot[2]
            data_time_univ = data_time + grabbed_time - self.start_time
            # Affect each value to the corresponding channel
            dict_chan_value = dict(zip(channels_in_selected_mode.split(','),list(zip(data_measurement,data_time_univ))))

            print('Chan :',Chan_to_plot)
            print('dict chan value : ',dict_chan_value)
        print('Data tot :',data_tot)
        print('Data measurement :',data_measurement)
        print('Data time :',data_time)
        print('Data time univ:',data_time_univ)
        print('Data time univ[0]:',data_time_univ[0])

        # Dictionary linking channel's modes to physical quantities
        dict_label_mode = {'VOLT:DC':'Voltage','VOLT:AC':'Voltage','CURR:DC':'Current','CURR:AC':'Current',
                        'RES':'Resistance','FRES':'Resistance','FREQ':'Frequency','TEMP':'Temperature'}

        # EMISSION OF DATA
        # When reading the scan_list, data are displayed and exported grouped by mode
        if self.controller.reading_scan_list == False:
            if DAQ_1DViewer_Keithley2700.panel == 'FRONT':
                labels= 'Front input'
            elif DAQ_1DViewer_Keithley2700.panel == 'REAR':
                labels=[Chan_to_plot[i] for i in range(len(Chan_to_plot))]
            # AXIS
            # x_axis = Axis(label='Time', units='s',data=np.array([data_time_univ[i] for i in range(len(data_time_univ))]),index=0)
            # y_value = np.array([data_measurement[i] for i in range(len(data_measurement))])
            x_axis = Axis(label='Time', units='s',data=np.array([data_time_univ[0]]),index=0)
            self.x_axis = x_axis
            y_value = np.array([data_measurement[0]])
            print('x_axis :',x_axis)
            print('type x :', type(x_axis.data))
            print('x :', x_axis.data)
            print('type y :', type(y_value))
            print('y :', y_value)
            
            # Grab data
            dwa = DataToExport(name='keithley2700',
                                            data=[DataFromPlugins(name=dict_label_mode[self.controller.current_mode],
                                                                    data=[np.array([data_measurement[i]]) for i in range(len(data_measurement))],
                                                                    x_axis=self.x_axis,
                                                                    dim='Data1D',
                                                                    labels=labels)])
            
        # Reading only channels configured in the selected mode
        elif self.controller.reading_scan_list == True:
            print('\n***************** DEBUG IN ********************')
            print('Modes + channels: ', self.controller.modes_channels_dict)
            print(' Channels + value ', dict_chan_value)
            for key in self.controller.modes_channels_dict.keys():
                if self.controller.modes_channels_dict.get(key) != []:
                    print('key = ',key)
                    for chan in self.controller.modes_channels_dict.get(key):
                        print('chan = ', chan)
                        print('str chan ', str(chan))
                        print(' dict chan value[str(chan)]', dict_chan_value[str(chan)])
                        print(' dict chan value.get(chan)', dict_chan_value.get(str(chan)))
            print('***************** DEBUG OUT ********************\n')

            data = [DataFromPlugins(name=dict_label_mode[key],
                                    data=[np.array([dict_chan_value[str(chan)][0]]) for chan in self.controller.modes_channels_dict.get(key)],
                                    axes=[Axis(label='Time',
                                               units='s',
                                               data=np.array([dict_chan_value[str(chan)][1]]),
                                               index=0)  for chan in self.controller.modes_channels_dict.get(key)],
                                    dim='Data1D',
                                    labels=['Channel ' + str(chan) for chan in self.controller.modes_channels_dict.get(key)]
                                    ) for key in self.controller.modes_channels_dict.keys() if self.controller.modes_channels_dict.get(key) \
                                        != []]
            data.append(DataFromPlugins(name='TEST',
                                        data=[np.random.randn(10,10)],
                                        axes=[Axis(label='Time', units='s',data=np.arange(10),index=0),
                                              Axis(label='Time', units='s',data=np.arange(10),index=0)],
                                        dim='Data1D',
                                        labels=['Arange test']))

            # Grab data (by scanning configured channels)
            dwa = DataToExport(name='keithley2700',data=data)
        
        self.dte_signal.emit(dwa)

    def stop(self):
        """Stop the current grab hardware wise if necessary"""
        self.start_time = None
        self.emit_status(ThreadCommand('Update_Status', ['Acquisition stoped']))
        return ''

if __name__ == '__main__':
    main(__file__)