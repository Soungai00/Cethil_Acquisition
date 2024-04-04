# import os
# import time
# import numpy as np
# from easydict import EasyDict as edict
# from pymodaq.utils.daq_utils import ThreadCommand
# from pymodaq.utils.data import Axis, DataFromPlugins, DataToExport
# from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
# from pymodaq.utils.parameter import Parameter

# from pymodaq_plugins_keithley2700 import config as k2700config
# from ...hardware.keithley2700_VISADriver import Keithley2700VISADriver as Keithley2700

# class DAQ_1DViewer_Keithley2700(DAQ_Viewer_base):
#     """ Keithley 2700 plugin class for a OD viewer.
    
#     This object inherits all functionalities to communicate with PyMoDAQ’s DAQ_Viewer module through inheritance via
#     DAQ_Viewer_base. It makes a bridge between the DAQ_Viewer module and the Python wrapper of a the keithley 2700.

#     * Keithley 27XX should be compatible with this plugin
#     * Tested with Keithley 2700 Multimeter/Switch System
#     * PyMoDAQ version = 4.0.11 during the test

#     Attributes:
#     -----------
#     controller: object
#         The particular object that allow the communication with the hardware, in general a python wrapper around the hardware library.
#     params: dictionnary list
#     x_axis: 1D numpy array
#     mode: str
    
#     """
#     # Read configuration file
#     rsrc_name = k2700config('INSTRUMENT').get('rsrc_name')
#     panel = k2700config('INSTRUMENT').get('panel').upper()
#     channels = k2700config('CHANNELS').keys()

#     if panel == 'FRONT':
#         print('Panel configuration 1D viewer:',panel)
#         params = comon_parameters+[
#             {'title': 'Keithley2700',  'name': 'K2700Params', 'type': 'group', 'children': [
#                 {'title': 'ID', 'name': 'ID', 'type': 'text', 'value': ''},
#                 {'title': 'FRONT panel', 'name': 'frontpanel', 'type': 'group', 'children': [
#                     {'title': 'Mode', 'name': 'frontmode', 'type': 'list', 'limits': ['VDC','VAC','IDC','IAC','R2W','R4W','FREQ','TEMP'], 'value': 'VDC'}]}
#             ]}
#         ]
#     elif panel == 'REAR':
#         print('Panel configuration 1D viewer:',panel)
#         params = comon_parameters+[
#             {'title': 'Keithley2700',  'name': 'K2700Params', 'type': 'group', 'children': [
#                 {'title': 'ID', 'name': 'ID', 'type': 'text', 'value': ''},
#                 {'title': 'REAR panel', 'name': 'rearpanel', 'type': 'group', 'children': [
#                     {'title': 'Mode', 'name': 'rearmode', 'type': 'list', 'limits': ['SCAN_LIST','VDC', 'VAC', 'IDC', 'IAC', 'R2W', 'R4W', 'FREQ', 'TEMP'], 'value': 'VDC'}
#                 ]}
#             ]}
#         ]

#     # Remove current measurement from parameters when non-amps modules
#     if Keithley2700(rsrc_name).non_amp_module == True:
#         params[1]['children'][0]['children'][0]['limits'] = [i for i in params[1]['children'][0]['children'][0]['limits'] if not 'IAC' in i and not 'IDC' in i]

#     def __init__(self, parent=None, params_state=None):
#         super(DAQ_1DViewer_Keithley2700, self).__init__(parent, params_state)
#         self.x_axis = None
#         self.channels_in_selected_mode = None
#         self.start_time = None

#     def commit_settings(self, param: Parameter):
#         """Apply the consequences of a change of value in the detector settings

#         Parameters
#         ----------
#         param: Parameter
#             A given parameter (within detector_settings) whose value has been changed by the user
#         """
#         if 'mode' in param.name():
#             """Updates the newly selected measurement mode"""
#             print('Parameter :',param.value())
#             # Read the configuration file to determine which mode to use
#             if DAQ_1DViewer_Keithley2700.panel == 'FRONT':
#                 value = param.value()
#                 self.controller.set_mode(value)
#             elif DAQ_1DViewer_Keithley2700.panel == 'REAR':
#                 value = 'SCAN_'+param.value()
#                 self.channels_in_selected_mode = self.controller.set_mode(value)
#                 print('Channels to plot :',self.channels_in_selected_mode)

#             print('DAQ_viewer command sent to keithley visa driver :',value)

#     def ini_detector(self, controller=None):
#         """Detector communication initialization

#         :param controller: Custom object of a PyMoDAQ plugin (Slave case). None if only one actuator/detector by controller (Master case)
#         :type controller: object


#         :return: info
#         :rtype: str

#         :return: info
#         :rtype: str

#         :return: initialized
#         :rtype: bool

#         :return: False if initialization failed otherwise True
        
#         """
#         print('Detector 1D initialized')

#         self.status.update(edict(initialized=False, info="", x_axis=None, y_axis=None, controller=None))
#         if self.settings.child(('controller_status')).value() == "Slave":
#             if controller is None: 
#                 raise Exception('no controller has been defined externally while this detector is a slave one')
#             else:
#                 self.controller = controller
#         else:
#             try:
#                 self.controller = Keithley2700(rsrc_name)
#             except Exception as e:
#                 raise Exception('No controller could be defined because an error occurred\
#                  while connecting to the instrument. Error: {}'.format(str(e)))
        
#         # Reset Keithley
#         self.controller.configuration_sequence()
#         txt = self.controller.get_idn()
#         self.settings.child('K2700Params','ID').setValue(txt)

#         # Initilize detector communication and set the default value (VDC)
#         if DAQ_1DViewer_Keithley2700.panel == 'FRONT':
#             value = self.settings.child('K2700Params', 'frontpanel', 'frontmode').value()
#             self.controller.set_mode(value)
#         elif DAQ_1DViewer_Keithley2700.panel == 'REAR':
#             value = 'SCAN_'+self.settings.child('K2700Params', 'rearpanel', 'rearmode').value()
#             self.channels_in_selected_mode = self.controller.set_mode(value)
#             print('Channels to plot :',self.channels_in_selected_mode)
#         print('DAQ_viewer command sent to keithley visa driver :',value)

#         # Get the x_axis
#         self.x_axis = Axis(label='Time', units='s',data=np.array([0]),index=0)

#         # # Initialize viewers with the future type of data
#         # self.dte_signal.emit(DataToExport(name='keithley2700',
#         #                                   data=[DataFromPlugins(name='Temperature_0D',
#         #                                                         data=[np.array([0])],
#         #                                                         dim='Data1D',
#         #                                                         labels=['M
#         # 
#         # eas', 'Time']),



#         #                                         DataFromPlugins(name='Temperature_1D',
#         #                                                         data=[np.array([0])],
#         #                                                         dim='Data1D',
#         #                                                         x_axis=self.x_axis,
#         #                                                         labels=['Meas', 'Time'])]))
        
#         # Initialize viewers with the future type of data
#         self.dte_signal.emit(DataToExport(name='keithley2700',
#                                           data=[DataFromPlugins(name='Temperature_1D',
#                                                                 data=[np.array([0])])]))
        
#         self.status.initialized = True
#         self.status.controller = self.controller
        
#         return self.status

#     def close(self):
#         """Terminate the communication protocol"""
#         self.controller.reset()
#         print('communication ended successfully')

#     def grab_data(self, Naverage=1, **kwargs):
#         """Start a grab from the detector

#         Parameters
#         ----------
#         Naverage: int
#             Number of hardware averaging (if hardware averaging is possible, self.hardware_averaging should be set to
#             True in class preamble and you should code this implementation)
#         kwargs: dict
#             others optionals arguments
#         """
#         if self.start_time == None:
#             self.start_time = time.time()
        
#         # TIME
#         grabbed_time = time.time()
#         print("Time : ", grabbed_time)
#         print('Start time :', self.start_time)
#         # ACQUISITION OF DATA
#         channels_in_selected_mode = self.channels_in_selected_mode
#         print('channels_in_selected_mode = ',channels_in_selected_mode)
#         if panel == 'FRONT':
#             data_measurement = self.controller.read()[1]
#             # data_red = self.controller.read()[1]
#             # data_measurement = data_red[:][1]
#             print('Data tot :',data_measurement)
#             print('Data tot[0][1] :',data_measurement[0][1])
#         elif panel == 'REAR':
#             Chan_to_plot=[]
#             for i in range(len(channels_in_selected_mode.split(','))):
#                 Chan_to_plot.append('Channel '+str(channels_in_selected_mode.split(',')[i]))
#             print(Chan_to_plot)
#             # data_measurement = self.controller.read()[1]
#             data_tot = self.controller.read()
#             print('Data tot :',data_tot)
#             data_measurement = data_tot[1]
#             print('Data measurement :',data_measurement)
#             data_time = data_tot[2]
#             print('Data time :',data_time)
#             data_time_univ = data_time + grabbed_time - self.start_time
#             print('Data time univ:',data_time_univ)
#             print('type time_univ :',type(data_time_univ))
#             print('Data time univ[0]:',data_time_univ[0])
#             print('type time_univ[0] :',type(data_time_univ[0]))
#             for i in range(len(Chan_to_plot)):
#                 print(Chan_to_plot[i]+': ',data_measurement[i])

#         # AXIS
#         # x_axis = Axis(label='Time', units='s',data=np.array([data_time_univ[i] for i in range(len(data_time_univ))]),index=0)
#         # y_value = np.array([data_measurement[i] for i in range(len(data_measurement))])
#         x_axis = Axis(label='Time', units='s',data=np.array([data_time_univ[0]]),index=0)
#         self.x_axis = x_axis
#         y_value = np.array([data_measurement[0]])
#         print('x_axis :',x_axis)
#         print('type x :', type(x_axis.data))
#         print('x :', x_axis.data)
#         print('type y :', type(y_value))
#         print('y :', y_value)

#         # EMISSION OF DATA
#         # self.dte_signal.emit(DataToExport(name='keithley2700',
#         #                                   data=[DataFromPlugins(name='Temperature_0D',
#         #                                                         data=[np.array([data_measurement[i]]) for i in range(len(data_measurement))],
#         #                                                         # data=y_value,
#         #                                                         dim='Data1D',
#         #                                                         labels=[Chan_to_plot[i] for i in range(len(Chan_to_plot))]),
#         #                                                         # labels=Chan_to_plot[0]),
#         #                                         DataFromPlugins(name='Temperature_1D',
#         #                                                         data=y_value,
#         #                                                         dim='Data1D',
#         #                                                         x_axis=self.x_axis,
#         #                                                         labels=Chan_to_plot[0])]))
        
#         self.dte_signal.emit(DataToExport(name='keithley2700',
#                                           data=[DataFromPlugins(name='Temperature_1D',
#                                                                 data=[data_measurement])]))
        
#         # SAVING DATA

#         # Write data in txt file
#         if not os.path.exists('Keithley2700_data_det1D.txt'):
#             open('Keithley2700_data_det1D.txt','w')
#         file = open('Keithley2700_data_det1D.txt','a')
#         for i in range(len(data_measurement)):
#             # file.write("%.2f" % str(data_time_univ[i])+'\t')
#             # file.write("%.2f" % str(data_measurement[i])+'\t')
#             file.write(str(data_time_univ[i])+'\t'+str(data_measurement[i])+'\t')
#         file.write('\n')
#         file.close()

#     def stop(self):
#         """Stop the current grab hardware wise if necessary"""
#         # self.controller.stop_acquisition() #Stop scan
#         self.start_time = None
#         self.emit_status(ThreadCommand('Update_Status', ['Acquisition stoped']))
#         return ''

# if __name__ == '__main__':
#     main(__file__)