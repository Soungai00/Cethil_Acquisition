import configparser

config = configparser.ConfigParser(allow_no_value=True)

config.add_section('CONFIG')
config.set('CONFIG','; Must set the absolute path of this configuration file in the 2 following files:')
config.set('CONFIG','; daq_viewer_plugins\plugins_0D\daq_0Dviewer_Keithley2700.py')
config.set('CONFIG','; hardware\keithley2700_VISADriver.py')
config.set('CONFIG','; Example of absolute path: C:\\Users\\[...]\\k2700config.ini')


config['INSTRUMENT'] = {}
config.set('INSTRUMENT','; modules')
config.set('INSTRUMENT','modules','7706')
config.set('INSTRUMENT','; resource name')
config['INSTRUMENT']['rsrc_name'] = 'ASRL1::INSTR'
config.set('INSTRUMENT','; termination character')
config['INSTRUMENT']['termination'] = 'LF'
# CR = Carriage Return = '\r', LF = Line Feed = '\n', CRLF = '\r\n', LFCR = '\n\r'
config.set('INSTRUMENT','; front/rear panel')
config['INSTRUMENT']['panel'] = 'REAR'

config.add_section('PARAMETERS')
config.set('PARAMETERS','; If more than 1, channels must be separated by a coma')
config.set('PARAMETERS','chan_to_read','101,102')
config.set('PARAMETERS','; Possible modes are VDC,VAC,IDC,IAC,R2W,R4W,FREQ and TEMP')
config.set('PARAMETERS','chan_mode','TEMP,VDC')


with open('k2700config.ini','w') as configfile:
    config.write(configfile)