import pyvisa as visa
import numpy as np
import time
import configparser

# Read configuration file
config = configparser.ConfigParser()
config.read('k2700config.ini')

# Termination character
if config['INTRUMENT']['termination'] == 'CR':
    termination = '\r'
elif config['INTRUMENT']['termination'] == 'LF':
    termination = '\n'
elif config['INTRUMENT']['termination'] == 'CRLF':
    termination = '\r\n'
elif config['INTRUMENT']['termination'] == 'LFCR':
    termination = '\n\r'

# Channel(s) to read
channels = '(@' + config['PARAMETERS']['chan_to_read'] + ')'

class Keithley2700VISADriver:
    """VISA class driver for the Keithley 2700 Multimeter/Switch System

    This class relies on pyvisa module to communicate with the instrument via VISA protocol
    Please refer to the instrument reference manual available at:
    https://download.tek.com/manual/2700-900-01K_Feb_2016.pdf

    """

    def __init__(self, rsrc_name, pyvisa_backend='@ivi'):
        """Initialize Keithley2700VISADriver class

        Parameters
        ----------
        rsrc_name:  string
            VISA Resource name
        pyvisa_backend: string
            Expects a pyvisa backend identifier or a path to the visa backend dll (ref. to pyvisa)
        
        """
        rm = visa.highlevel.ResourceManager(pyvisa_backend)
        self._instr = rm.open_resource(rsrc_name)

        # Config of the termination character
        self._instr.write_termination = termination
        self._instr.read_termination = termination
        # For scanning, timeout needs to be higher
        self._instr.timeout = 5000

    def close(self):
        self._instr.close()

    def reset(self):
        # Clear measurement event register
        self._instr.write("*CLS")
        # One-shot measurement mode (Equivalent to INIT:COUNT OFF)
        self._instr.write("*RST")

    def clear_buffer(self):
        # Default: auto clear when scan start
        self._instr.write("TRAC:CLE")

    def clear_buffer_on(self):
        # Disable buffer auto clear
        self._instr.write("TRAC:CLE:AUTO ON")

    def clear_buffer_off(self):
        # Disable buffer auto clear
        self._instr.write("TRAC:CLE:AUTO OFF")
    
    def initconton(self):
        # Enable continuous initiation
        self._instr.write("INIT:CONT ON")

    def initcontoff(self):
        # Disable continuous initiation
        self._instr.write("INIT:CONT OFF")

    def get_idn(self):
        # Query identification
        return self._instr.query("*IDN?")
    
    def read(self):
        # Read command performs 3 actions (equivalent to ABORT,INIT,FETCH?)
        str_all = self._instr.query("READ?")
        # print('str_all = ',str_all)
        # Split the instrument answer and remove non-digit characters (units)
        split_str = str_all.split(",")
        # Select only the measured value not looking at the time and reading count
        quantities = split_str[::3]
        # print('quantities = ',quantities)
        str_values = ''
        for j in range(len(quantities)):
            if not j==0:
                str_values += ','
            for l in range(len(quantities[j])):
                test_carac = quantities[j][-(l+1)]
                if test_carac.isdigit() == True:
                    if l==0:   
                        str_values += quantities[j]
                    else:
                        str_values += quantities[j][:-l]
                    break
        # Split the created string to access each value
        values = str_values.split(",")
        # Create a numpy.array containing desired values (float type)
        values_array = np.array(values,dtype=float)
        # Return a list of each value stored in the buffer
        return str_all,values_array

    def fetch(self):
        # Return the latest available reading
        str_all = self._instr.query("FETCH?")
        # print('str_all = ',str_all)
        # Split the instrument answer and remove non-digit characters (units)
        split_str = str_all.split(",")
        # Select only the measured value not looking at the time and reading count
        quantities = split_str[::3]
        # print('quantities = ',quantities)
        str_values = ''
        for j in range(len(quantities)):
            if not j==0:
                str_values += ','
            for l in range(len(quantities[j])):
                test_carac = quantities[j][-(l+1)]
                if test_carac.isdigit() == True:
                    if l==0:   
                        str_values += quantities[j]
                    else:
                        str_values += quantities[j][:-l]
                    break
        # Split the created string to access each value
        values = str_values.split(",")
        # Create a numpy.array containing desired values (float type)
        values_array = np.array(values,dtype=float)
        # Return a list of each value stored in the buffer
        return str_all,values_array

    def data(self):
        str_all = self._instr.query("TRAC:DATA?")
        # print('str_all = ',str_all)
        # Split the instrument answer and remove non-digit characters (units)
        split_str = str_all.split(",")
        # Select only the measured value not looking at the time and reading count
        quantities = split_str[::3]
        # print('quantities = ',quantities)
        str_values = ''
        for j in range(len(quantities)):
            if not j==0:
                str_values += ','
            for l in range(len(quantities[j])):
                test_carac = quantities[j][-(l+1)]
                if test_carac.isdigit() == True:
                    if l==0:   
                        str_values += quantities[j]
                    else:
                        str_values += quantities[j][:-l]
                    break
        # Split the created string to access each value
        values = str_values.split(",")
        # Create a numpy.array containing desired values (float type)
        values_array = np.array(values,dtype=float)
        # Return a list of each value stored in the buffer
        return str_all,values_array
    
    def define_input(self, input):
        return str(input)
    
    def stop_acquisition(self):
        # If scan in process, stop it
        self._instr.write("ROUT:SCAN:LSEL NONE")
    
    def set_mode(self, mode, **kwargs):
        """

        Parameters
        ----------
        mode : string
            Measurement configuration ('VDC', 'VAC', 'IDC', 'IAC', 'R2W', 'R4W', 'FREQ' and 'TEMP' modes are supported)
        kwargs :  dict
            Used to pass optional arguments
            - Autorange "RANG:AUTO <b>" <b> = ON/OFF
            - Range ":RANG: <n>"
            - Display resolution ":DIG <n>" <n> = 3.5, 4.5, 5.5 or 6.5
            - Number of power line cycles ":NPLC <n>"

        """
        cmd = 'FUNC '
        if "VDC" in mode:
            cmd += "'VOLT:DC'"
            conf = "VOLT"
        elif "VAC" in mode:
            cmd += "'VOLT:AC'"
            conf = "VOLT"
        elif "IDC" in mode:
            cmd += "'CURR:DC'"
            conf = "CURR"
        elif "IAC" in mode:
            cmd += "'CURR:AC'"
            conf = "CURR"
        elif "R2W" in mode:
            cmd += "'RES'"
            conf = "RES"
        elif "R4W" in mode:
            cmd += "'FRES'"
            conf = "FRES"
        elif "FREQ" in mode:
            cmd += "'FREQ'"
            conf = "FREQ"
        elif "TEMP" in mode:
            cmd += "'TEMP'"
            conf = "TEMP"

        # Instructions to be sent
        if "SCAN" not in mode:
            self._instr.write(cmd)
        else:
            self.reset()
            self.clear_buffer()
            cmd += "," + channels
            print('Command sent :',cmd)
            self._instr.write(cmd)
            if "SCAN_TEMP" in mode:
                self._instr.write("TEMP:TRAN TC," + channels)
                self._instr.write("TEMP:TC:TYPE K," + channels)
                self._instr.write("TEMP:RJUN:RSEL INT," + channels)
            # Set scan list channels
            self._instr.write("ROUT:SCAN " + channels)
            # Start scan immediately when enabled and triggered
            self._instr.write("ROUT:SCAN:TSO IMM")
            # Enable scan
            self._instr.write("ROUT:SCAN:LSEL INT")
            # Test init contiuous disabled
            self.initcontoff()
            # Set to perform 1 to INF scan(s)
            self._instr.write("TRIG:COUN 1")
            # Set to scan <n> channels
            samp_count = 1+channels.count(',')
            self._instr.write("SAMP:COUN "+str(samp_count))
            # Trigger immediately after previous scan end
            self._instr.write("TRIG:SOUR IMM")
            # Use timmer to trigger <n> seconds after previous scan end
            # k2700._instr.write("TRIG:SOUR TIM")
            # k2700._instr.write("TRIG:TIM 0.01")
            
        # Config
        if 'range' in kwargs.keys():
            self._instr.write(conf+':RANG '+str(kwargs['range']))
        if 'autorange' in kwargs.keys():
            self._instr.write(conf+':RANG:AUTO '+str(kwargs['autorange']))
        if 'resolution' in kwargs.keys():
            self._instr.write(conf+':DIG '+str(kwargs['resolution']))
        if 'NPLC' in kwargs.keys():
            self._instr.write(conf+':NPLC '+str(kwargs['NPLC']))


if __name__ == "__main__":
    try:

        print("In main")

        k2700 = Keithley2700VISADriver("ASRL1::INSTR")
        print("IDN?")
        print(k2700.get_idn())


        # SETTINGS
        ##########
        # k2700.set_mode("VDC", range=0.1, resolution=4.5, NPLC=3)
        # k2700.set_mode("VAC", autorange="on", resolution=6.5)
        # k2700.set_mode("IDC", autorange="off", resolution="MIN")
        # k2700.set_mode("IAC", range=10, resolution="MAX")
        # k2700.set_mode("Ohm2")
        # k2700.set_mode("R4W")
        # k2700.set_mode("FREQ")
        # k2700.set_mode("TEMP")


        # CONTINUOUS TRIGGERING TEST
        ############################
        # k2700._instr.write("SYST:PRES")
        # k2700._instr.write("FUNC 'TEMP'")
        # print(k2700._instr.query("DATA?"))


        # ONE-SHOT TRIGGERING TEST
        # ########################
        # k2700.reset()
        # k2700.set_mode("TEMP")
        # print("Variable's type returned by read function: ",type(k2700._instr.query("READ?"))
        # print(k2700._instr.query("READ?"))
        # k2700.set_mode("Ohm2")
        # k2700._instr.write("RES:RANG 1e3")
        # print(k2700._instr.query("READ?"))


        # MODEL 7700 SWITCHING MODULE TESTS
        # #################################
        # One-shot measurement mode
        # k2700.reset()
        # Select temp function
        # k2700.set_mode("TEMP")
        # Select thermocouple transducer
        # k2700._instr.write("TEMP:TRAN TC")
        # Select type K thermocouple
        # k2700._instr.write("TEMP:TC:TYPE K")
        # Select internal junction
        # k2700._instr.write("TEMP:RJUN:RSEL INT")
        # Close channel(s)
        # k2700._instr.write("ROUT:CLOS " + channels)
        # Trigger one measurement
        # k2700._instr.write("INIT")
        # Return measured reading
        # print("One-shot measurement DATA: ",k2700._instr.query("DATA?"))


        # MODEL 7700 SCAN CONFIGURATION TESTS
        # ###################################
        k2700.reset()

        # Temperature tests
        k2700._instr.write("FUNC 'TEMP', " + channels)
        k2700._instr.write("TEMP:TRAN TC, " + channels)
        k2700._instr.write("TEMP:TC:TYPE K, " + channels)
        k2700._instr.write("TEMP:RJUN:RSEL INT, " + channels)

        # Voltage tests
        # k2700._instr.write("FUNC 'VOLT:DC', " + channels)

        # Set scan list channels
        k2700._instr.write("ROUT:SCAN " + channels)
        print('Rout scan ? :', k2700._instr.query("ROUT:SCAN?"))
        # Start scan immediately when enabled and triggered, default : IMM
        k2700._instr.write("ROUT:SCAN:TSO IMM")
        # Enable scan
        k2700._instr.write("ROUT:SCAN:LSEL INT")
        k2700.clear_buffer()

        # IF INIT COUNT OFF
        k2700.initcontoff()
        # Set to perform 1 to INF scan(s)
        k2700._instr.write("TRIG:COUN INF")
        # Set to scan <n> channels
        k2700._instr.write("SAMP:COUN 6")
        # Trigger immediately after previous scan end
        k2700._instr.write("TRIG:SOUR IMM")
        # Use timmer to trigger <n> seconds after previous scan end
        # k2700._instr.write("TRIG:SOUR TIM")
        # k2700._instr.write("TRIG:TIM 5")

        # Set buffer parameters
        # k2700._instr.write("TRAC:POIN 20")
        # k2700._instr.write("TRAC:FEED SENS")
        # k2700._instr.write("TRAC:FEED:CONT NEXT")

        # EITHER
        # # Initiate scan cycle(s)
        # k2700._instr.write("INIT")
        # # Need to wait until buffer is filled before reading data
        # time.sleep(3)
        # # Return data stored in the buffer (if more than 1 cycle, only last cycle
        # # because each scan clear buffer)
        # data = k2700.data()[0]
        # print("All data from buffer, empty if no time sleep:")
        # print(data)
        # datavalue = k2700.data()[1]
        # print("Values from buffer:")
        # print(datavalue)

        # OR
        # Each READ command initiate one scan cycle and request sample readings
        print("Below a loop with the query READ? :")
        for i in range(2):
            print('string with all data :')
            print(k2700.read()[0])
            print('string with values only :')
            print(k2700.read()[1])

        # # IF INIT COUNT ON
        # k2700.initconton()
        # k2700._instr.write("SAMP:COUN 1")
        # # Read last reading
        # for i in range(3):
        #     data = k2700.fetch()[1]
        #     print("Reading:\n",data)
        #     time.sleep(2)

        # Stop the scan
        k2700._instr.write("ROUT:SCAN:LSEL NONE")

        k2700.clear_buffer()
        k2700.close()
        print("Out")

    except Exception as e:
        print("Exception ({}): {}".format(type(e), str(e)))
