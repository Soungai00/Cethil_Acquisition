import pyvisa as visa
import time

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
        rsrc_name   (string)        VISA Resource name
        pyvisa_backend  (string)    Expects a pyvisa backend identifier or a path to the visa backend dll (ref. to pyvisa)
        
        """
        rm = visa.highlevel.ResourceManager(pyvisa_backend)
        self._instr = rm.open_resource(rsrc_name)

        self._instr.write_termination = '\n'
        self._instr.read_termination = '\n'
        # For scanning tests
        # self._instr.timeout = 5000

    def close(self):
        self._instr.close()

    def reset(self):
        # Clear measurement event register
        self._instr.write("*CLS")
        # One-shot measurement mode (Equivalent to INIT:COUNT OFF)
        self._instr.write("*RST")
    
    def clear_buffer(self):
        # Default: auto clear when scan start but can set "TRAC:CLE:AUTO OFF"
        self._instr.write("TRAC:CLE")
    
    def initcontoff(self):
        self._instr.write("INIT:CONT OFF")

    def get_idn(self):
        return self._instr.query("*IDN?")
    
    def read(self):
        return self._instr.query("READ?")
    
    def readvalue(self):
        str_query = self._instr.query("READ?")
        # Split the instrument answer and remove non-digit characters (units)
        split_str = str_query.split(",")
        quantity = split_str[0]
        for i in range(len(quantity)):
            test_carac = quantity[-(i+1)]
            if test_carac.isdigit() == True:
                if i==0:   
                    value = quantity
                else:
                    value = quantity[:-i]
                break
        # Return a float value without any unit
        return float(value)

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
        if mode == "Ohm2" or mode == "R2W":
            cmd += "'RES'"
            conf = "RES"
        elif mode == "Ohm4" or mode == "R4W":
            cmd += ""'FRES'""
            conf = "FRES"
        elif mode == "VDC" or mode == "V":
            cmd += "'VOLT:DC'"
            conf = "VOLT"
        elif mode == "VAC":
            cmd += "'VOLT:AC'"
            conf = "VOLT"
        elif mode == "IDC" or mode == "I":
            cmd += "'CURR:DC'"
            conf = "CURR"
        elif mode == "IAC":
            cmd += "'CURR:AC'"
            conf = "CURR"
        elif mode == "FREQ":
            cmd += "'FREQ'"
            conf = "FREQ"
        elif "TEMP" in mode:
            cmd += "'TEMP'"
            if "@" in mode:
                cmd += mode.split(",")[1]
            else:
                conf = "TEMP"
        
        # Mode
        self._instr.write(cmd)

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

        print("In")

        k2700 = Keithley2700VISADriver("ASRL1::INSTR")
        print("IDN?")
        print(k2700.get_idn())
        k2700.reset()

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
        # print("Variable's type returned by read function: ",type(k2700.read()))
        # print(k2700.read())
        # print("Variable's type returned by readvalue function: ",type(k2700.readvalue()))
        # print(k2700.readvalue())
        # k2700.set_mode("Ohm2")
        # k2700._instr.write("RES:RANG 1e3")
        # print(k2700.read())

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
        # Close channel 101
        # k2700._instr.write("ROUT:CLOS (@101)")
        # Trigger one measurement
        # k2700._instr.write("INIT")
        # Return measured reading
        # print("One-shot measurement DATA: ",k2700._instr.query("DATA?"))

        # MODEL 7700 SCAN CONFIGURATION TESTS
        # ###################################
        k2700.clear_buffer()
        k2700.initcontoff()
        k2700._instr.write("TRIG:SOUR TIM")
        k2700._instr.write("TRIG:TIM 0.1")
        # k2700._instr.write("FUNC 'TEMP', (@101:120)")
        k2700._instr.write("FUNC 'TEMP', (@101,102)")
        k2700._instr.write("TEMP:TRAN TC, (@101,102)")
        k2700._instr.write("TEMP:TC:TYPE K, (@101,102)")
        k2700._instr.write("TEMP:RJUN:RSEL INT, (@101,102)")
        # Set to perform 1 scan
        k2700._instr.write("TRIG:COUN 5")
        # Set to scan 20 channels
        k2700._instr.write("SAMP:COUN 2")
        # Set scan list channels
        k2700._instr.write("ROUT:SCAN (@101,102)")
        # Start scan immediately when enabled and triggered
        k2700._instr.write("ROUT:SCAN:TSO IMM")
        # Enable scan
        k2700._instr.write("ROUT:SCAN:LSEL INT")

        # k2700._instr.write("ROUT:CLOS (@101)")

        # k2700._instr.write("FUNC 'RES', (@102)")
        # k2700._instr.write("ROUT:CLOS (@102)")

        # k2700._instr.write("FUNC 'VOLT:DC', (@104)")
        # k2700._instr.write("FUNC 'RES', (@112,113,114)")
        # k2700._instr.write("ROUT:SCAN (@101,102,104)")

        # Initiate one scan cycle
        # k2700._instr.write("INIT")
        # time.sleep(5)
        # Read buffer readings
        # data = k2700._instr.query("TRAC:DATA?")
        # print("DATA from buffer:\n",data.replace("#,","#\n"))

        # Initiate one scan cycle and request sample readings
        # dataread = k2700._instr.query("SENS:DATA:FRES?")
        dataread = k2700._instr.query("READ?")
        print("DATA from sample reading: ", dataread)
        k2700.clear_buffer()
        k2700.close()
        print("Out")

    except Exception as e:
        print("Exception ({}): {}".format(type(e), str(e)))
