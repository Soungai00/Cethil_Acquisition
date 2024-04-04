import numpy as np
import pyvisa as visa
import time
from pymodaq_plugins_keithley2700 import config as k2700config

class Keithley2700VISADriver:
    """VISA class driver for the Keithley 2700 Multimeter/Switch System

    This class relies on pyvisa module to communicate with the instrument via VISA protocol.
    Please refer to the instrument reference manual available at:
    https://download.tek.com/manual/2700-900-01K_Feb_2016.pdf

    """

    def __init__(self, rsrc_name, pyvisa_backend='@ivi'):
        """Initialize Keithley2700VISADriver class

        :param rsrc_name: VISA Resource name
        :type rsrc_name: string

        :param pyvisa_backend: Expects a pyvisa backend identifier or a path to the visa backend dll (ref. to pyvisa)
        :type pyvisa_backend: string
        
        :attribute _instr: Resource name opened by resource manager
        :type _instr: pyvisa.resources.serial.SerialInstrument
        """
        rm = visa.highlevel.ResourceManager(pyvisa_backend)
        self._instr = rm.open_resource(rsrc_name)
        self._instr.timeout = 10000

        # Termination character
        termination_dictionary = {'CR':'\r','LF':'\n','CRLF':'\r\n','LFCR':'\n\r'}
        self._instr.write_termination = termination_dictionary.get(k2700config('INSTRUMENT').get('termination'))
        self._instr.read_termination = termination_dictionary.get(k2700config('INSTRUMENT').get('termination'))

        # Non-amps modules
        self.non_amp_module = False
        non_amp_modules_list = [7701,7703,7706,7707,7708,7709]
        if k2700config('MODULE','module_name') in non_amp_modules_list:
            self.non_amp_module = True

        # Channels & modes attributes
        self.channels_scanlist = ''
        self.modes_channels_dict = {'VOLT:DC':[],'VOLT:AC':[],'CURR:DC':[],'CURR:AC':[],'RES':[],'FRES':[],'FREQ':[],'TEMP':[]}
        self.sample_count_1 = False
        self.reading_scan_list = False
        self.current_mode = ''

    def configuration_sequence(self):
        """Configure each channel selected by the user

        Read the configuration file to get the channels used and their configuration, and send the keithley a sequence allowing to set up each channel.
        
        :raises TypeError: Channel section of configuration file not correctly defined, each channel should be a dictionary
        :raises ValueError: Channel not correctly defined, it should at least contain a key called "mode"

        """
        print('\n********** CONFIGURATION SEQUENCE INITIALIZED **********')
        print('Acquisition card = ', k2700config('MODULE','module_name'))

        self.reset()
        self.clear_buffer()
        channels = ''

        # The following loop set up each channel in the config file
        for key in k2700config('CHANNELS').keys():

            # Raise error if the channels config section is not correctly set up by the user
            if not type(k2700config('CHANNELS',key))==dict:
                raise TypeError("Channel %s not correctly defined, should be a dict" % key)
            if not "mode" in k2700config('CHANNELS',key):
                print("Channel %s not fully defined, 'mode' is missing" % key)
                continue

            # Channel mode
            mode = k2700config('CHANNELS',key).get('mode').upper()
            self.modes_channels_dict[mode].append(int(key))
            channel = '(@' + key + ')'
            channels += key + ","
            cmd = "FUNC '" + mode + "'," + channel
            self._instr.write(cmd)

            # Console info
            print('Channel %s \n %s' % (key,k2700config('CHANNELS',key)))

            # Config
            if 'range' in k2700config('CHANNELS',key).keys():
                range = k2700config('CHANNELS',key).get('range')
                if 'autorange' in str(range):
                    self._instr.write(mode + ':RANG:AUTO ')
                else:
                    self._instr.write(mode + ':RANG ' + str(range))
                    
            if 'resolution' in k2700config('CHANNELS',key).keys():
                resolution = k2700config('CHANNELS',key).get('resolution')
                self._instr.write(mode + ':DIG ' + str(resolution))

            if 'nplc' in k2700config('CHANNELS',key).keys():
                nplc = k2700config('CHANNELS',key).get('nplc')
                self._instr.write(mode + ':NPLC ' + str(nplc))

            if "TEMP" in mode:
                transducer = k2700config('CHANNELS',key).get('transducer').upper()
                if "TC" in transducer:
                    tc_type = k2700config('CHANNELS',key).get('type').upper()
                    ref_junction = k2700config('CHANNELS',key).get('ref_junction').upper()
                    self.mode_temp_tc(channel,transducer,tc_type,ref_junction)
                elif "THER":
                    ther_type = k2700config('CHANNELS',key).get('type').upper()
                    self.mode_temp_ther(channel,transducer,ther_type)
                elif "FRTD":
                    frtd_type = k2700config('CHANNELS',key).get('type').upper()
                    self.mode_temp_frtd(channel,transducer,frtd_type)

            # Timeout update for long measurement modes such as voltage AC
            if "AC" in mode:
                self._instr.timeout += 4000
            # Handling errors
            current_error = self.get_error()
            try:
                if current_error != '0,"No error"':
                    raise ValueError("The following error has been raised by the Keithley: %s => Pease refer to the User Manual to correct it\n\
                                     Note: To make sure channels are well configured in the .toml file, refer to section 15 'SCPI Reference Tables', Table 15-5" % current_error)
            except Exception as e:
                print(e)
                pass
        
        self.current_mode = 'scan_list'
        self.channels_scanlist =  channels[:-1]
        print('********** CONFIGURATION SEQUENCE SUCCESSFULLY ENDED **********\n')

    def clear_buffer(self):
        # Default: auto clear when scan start
        self._instr.write("TRAC:CLE")

    def clear_buffer_off(self):
        # Disable buffer auto clear
        self._instr.write("TRAC:CLE:AUTO OFF")

    def clear_buffer_on(self):
        # Disable buffer auto clear
        self._instr.write("TRAC:CLE:AUTO ON")

    def close(self):
        self._instr.close()

    def data(self):
        if self.sample_count_1 == False:
            # Initiate scan
            self._instr.write("INIT")
            # Trigger scan
            self._instr.write("*TRG")
            # Get data (equivalent to TRAC:DATA? from buffer)
            str_answer = self._instr.query("FETCH?")
        else:
            str_answer = self._instr.query("READ?")
        # Split the instrument answer (MEASUREMENT,TIME,READING COUNT) to create a list
        list_split_answer = str_answer.split(",")

        # MEASUREMENT & TIME EXTRACTION
        list_measurements = list_split_answer[::3]
        str_measurements = ''
        list_times = list_split_answer[1::3]
        str_times = ''
        for j in range(len(list_measurements)):
            if not j==0:
                str_measurements += ','
                str_times += ','
            for l in range(len(list_measurements[j])):
                test_carac = list_measurements[j][-(l+1)]
                # Remove non-digit characters (units)
                if test_carac.isdigit() == True:
                    if l==0:   
                        str_measurements += list_measurements[j]
                    else:
                        str_measurements += list_measurements[j][:-l]
                    break
            for l in range(len(list_times[j])):
                test_carac = list_times[j][-(l+1)]
                # Remove non-digit characters (units)
                if test_carac.isdigit() == True:
                    if l==0:   
                        str_times += list_times[j]
                    else:
                        str_times += list_times[j][:-l]
                    break

        # Split created string to access each value
        list_measurements_values = str_measurements.split(",")
        list_times_values = str_times.split(",")
        # Create numpy.array containing desired values (float type)
        array_measurements_values = np.array(list_measurements_values,dtype=float)
        if self.sample_count_1 != True:
            array_times_values = np.array(list_times_values,dtype=float)
        else:
            array_times_values = np.array([0],dtype=float)

        return str_answer,array_measurements_values,array_times_values

    def define_input(self, input):
        return str(input)
    
    def get_error(self):
        # Ask the keithley to return the last current error
        return self._instr.query("SYST:ERR?")
    
    def get_idn(self):
        # Query identification
        return self._instr.query("*IDN?")
    
    def initcontoff(self):
        # Disable continuous initiation
        self._instr.write("INIT:CONT OFF")
        
    def initconton(self):
        # Enable continuous initiation
        self._instr.write("INIT:CONT ON")

    def mode_temp_frtd(self,channel,transducer,frtd_type,):
        self._instr.write("TEMP:TRAN " + transducer + "," + channel)
        self._instr.write("TEMP:FRTD:TYPE " + frtd_type + "," + channel)

    def mode_temp_tc(self,channel,transducer,tc_type,ref_junction):
        self._instr.write("TEMP:TRAN " + transducer + "," + channel)
        self._instr.write("TEMP:TC:TYPE " + tc_type + "," + channel)
        self._instr.write("TEMP:RJUN:RSEL " + ref_junction + "," + channel)

    def mode_temp_ther(self,channel,transducer,ther_type,):
        self._instr.write("TEMP:TRAN " + transducer + "," + channel)
        self._instr.write("TEMP:THER:TYPE " + ther_type + "," + channel)
    
    def reset(self):
        # Clear measurement event register
        self._instr.write("*CLS")
        # One-shot measurement mode (Equivalent to INIT:COUNT OFF)
        self._instr.write("*RST")

    def set_mode(self, mode):
        """Define whether the Keithley will scan all the scanlist or only channels in the selected mode

        :param mode: Measurement configuration ('SCAN_LIST', 'VDC', 'VAC', 'IDC', 'IAC', 'R2W', 'R4W', 'FREQ' and 'TEMP' modes are supported)
        :type mode: string

        """
        mode = mode.upper()
        
        # FRONT panel
        if "SCAN" not in mode:
            self._instr.write("FUNC " + mode)

        # REAR panel
        else:
            self.clear_buffer()
            # Init contiuous disabled
            self.initcontoff()
            mode = mode[5:]
            self.current_mode = mode
            if 'SCAN_LIST' in mode:
                self.reading_scan_list = True
                self.sample_count_1 = False
                channels = '(@' + self.channels_scanlist + ')'
                # Set to perform 1 to INF scan(s)
                self._instr.write("TRIG:COUN 1")
                # Trigger immediately after previous scan end if IMM
                self._instr.write("TRIG:SOUR BUS")
                # Set to scan <n> channels
                samp_count = 1 + channels.count(',')
                self._instr.write("SAMP:COUN "+str(samp_count))
                # Disable scan if currently enabled
                self._instr.write("ROUT:SCAN:LSEL NONE")
                # Set scan list channels
                self._instr.write("ROUT:SCAN " + channels)
                # Start scan immediately when enabled and triggered
                self._instr.write("ROUT:SCAN:TSO IMM")
                # Enable scan
                self._instr.write("ROUT:SCAN:LSEL INT")


            else:
                self.reading_scan_list = False
                # Select channels in the channels list (config file) matching the requested mode
                channels = '(@' + str(self.modes_channels_dict.get(mode))[1:-1] + ')'
                # Set to perform 1 to INF scan(s)
                self._instr.write("TRIG:COUN 1")
                # Set to scan <n> channels
                samp_count = 1+channels.count(',')
                self._instr.write("SAMP:COUN "+str(samp_count))
                if samp_count == 1:
                    self.sample_count_1 = True
                    # Trigger definition
                    self._instr.write("TRIG:SOUR IMM")
                    # Disable scan if currently enabled
                    self._instr.write("ROUT:SCAN:LSEL NONE")
                    self._instr.write("ROUT:CLOS " + channels)
                else:
                    self.sample_count_1 = False
                    # Trigger definition
                    self._instr.write("TRIG:SOUR BUS")
                    # Disable scan if currently enabled
                    self._instr.write("ROUT:SCAN:LSEL NONE")
                    # Set scan list channels
                    self._instr.write("ROUT:SCAN " + channels)
                    # Start scan immediately when enabled and triggered
                    self._instr.write("ROUT:SCAN:TSO IMM")
                    # Enable scan
                    self._instr.write("ROUT:SCAN:LSEL INT")
                
            return(channels)
        
    def stop_acquisition(self):
        # If scan in process, stop it
        self._instr.write("ROUT:SCAN:LSEL NONE")

    def user_command(self):
        command = input('Enter here a command you want to send directly to the Keithley [if None, press enter]: ')
        if command != '':
            if command[-1] == "?":
                print(k2700._instr.query(command))
            else:
                k2700._instr.write(command)
            command = self.user_command()

if __name__ == "__main__":
    try:
        print("In main")

        k2700 = Keithley2700VISADriver("ASRL1::INSTR")
        print("IDN?")
        print(k2700.get_idn())
        
        k2700.reset()
        k2700.configuration_sequence()

        # Daq_viewer simulation first run
        k2700.set_mode(str(input('Enter which mode you want to scan [scan_scan_list, scan_volt:dc, scan_r2w, scan_temp...]:')))
        print('Manual scan example: >init >*trg >trac:data?')
        k2700.user_command()

        for i in range(2):
            print(k2700.data())
        print(k2700.data())

        # Daq_viewer simulation change mode
        k2700.user_command()
        k2700.set_mode(str(input('Enter which mode you want to scan [scan_scan_list, scan_volt:dc, scan_r2w, scan_temp...]:')))
        print('Manual scan example: >init >*trg >trac:data?')

        for i in range(2):
            print(k2700.data())
        print(k2700.data())

        k2700.clear_buffer()
        k2700.close()
        print("Out")

    except Exception as e:
        print("Exception ({}): {}".format(type(e), str(e)))
