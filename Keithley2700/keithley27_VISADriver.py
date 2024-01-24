import pyvisa as visa


class Keithley2110VISADriver:
    """
        VISA class driver for the Keithley 2110  5 1/2 Digit DMM
        This class relies on pyvisa module to communicate with the instrument via VISA protocol
        Please refer to the instrument reference manual available at:
        https://download.tek.com/manual/2110-901-01(C-Aug2013)(Ref).pdf
    """
    def __init__(self, rsrc_name, pyvisa_backend='@ivi'):
    # def __init__(self, rsrc_name):
        """
        Parameters
        ----------
        rsrc_name   (string)        VISA Resource name
        pyvisa_backend  (string)    Expects a pyvisa backend identifier or a path to the visa backend dll (ref. to pyvisa)
        """
        rm = visa.highlevel.ResourceManager(pyvisa_backend)
        rsrc_name = 'ASRL1::INSTR'
        self._instr = rm.open_resource(rsrc_name)
        #self._instr.reset()

        self._instr.read_termination = '\n'
        self._instr.write_termination = '\n'

    def close(self):
        self._instr.close()

    def get_identification(self):
        self._instr.query("*IDN?")
    
    def get_idn(self):
        return self._instr.query("*IDN?")

    def reset(self):
        self._instr.write("*CLS")
        self._instr.write("*RST")

    def read(self):
        return self._instr.query("READ?")
    
    def initcontoff(self):
        self._instr.write("INIT:CONT OFF")
    
    def readvalue(self):
        str_query = self._instr.query("READ?")
        # print(str_query)
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
    
    def fetch(self):
        return self._instr.query("FETCH?")
    
    def fetchvalue(self):
        str_query = self._instr.query("FETCH?")
        # print(str_query)
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
        mode    (string)    Measurement configuration ('VDC', 'VAC', 'IDC', 'IAC', 'R2W' and 'R4W' modes are supported)
        kwargs  (dict)      Used to pass optional arguments ('range' and 'resolution' are the only supported keys)

        Returns
        -------

        """
        assert (isinstance(mode, str))
        mode = mode.lower()

        cmd = 'FUNC '

        if mode == "Ohm2".lower() or mode == "R2W".lower():
            cmd += "'RES'"
        elif mode == "Ohm4".lower() or mode == "R4W".lower():
            cmd += "FRES"
        elif mode == "VDC".lower() or mode == "V".lower():
            cmd += "'VOLT:DC'"
        elif mode == "VAC".lower():
            cmd += "VOLT:AC"
        elif mode == "IDC".lower() or mode == "I".lower():
            cmd += "CURR:DC"
        elif mode == "IAC".lower():
            cmd += "CURR:AC"
        elif mode == "TEMP".lower():
            cmd += "'TEMP'"

        if 'range' in kwargs.keys():
            cmd += ' ' + str(kwargs['range'])
            if 'resolution' in kwargs.keys():
                cmd += ',' + str(kwargs['resolution'])
        elif 'resolution' in kwargs.keys():
            cmd += ' DEF,' + str(kwargs['resolution'])

        self._instr.write(cmd)


if __name__ == "__main__":
    try:
        
        print("In")
        k2110 = Keithley2110VISADriver('ASRL1::INSTR')
        k2110.reset()
        print("IDN?")
        print(k2110.get_idn())
        
        k2110.set_mode('Ohm2')
        print("Resistance reading test :")
        print(type(k2110.read()))
        print(k2110.readvalue())

        #k2110.set_mode('R4W', range=10, resolution='MAX')
        #k2110.set_mode('R4W', resolution='MIN')
        #k2110.set_mode('IAC', range=0.001, resolution='MIN')
        #k2110.set_mode('vdc', range=0.1, resolution='0.0001')

        k2110.set_mode('TEMP')
        print("Temperature reading test :")
        print(type(k2110.read()))
        print(k2110.readvalue())
        print("Temperature fetch test :")
        print(k2110.fetchvalue())        

        print("Out")
        k2110.close()

    except Exception as e:
        print("Exception ({}): {}".format(type(e), str(e)))
