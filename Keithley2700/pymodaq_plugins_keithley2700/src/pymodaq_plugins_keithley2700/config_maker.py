import configparser

config = configparser.ConfigParser(allow_no_value=True)

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