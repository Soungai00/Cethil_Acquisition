import configparser

config = configparser.ConfigParser()

config['INTRUMENT'] = {}
# Resource name
config['INTRUMENT']['rsrc_name'] = 'ASRL1::INSTR'
# Termination character
config['INTRUMENT']['termination'] = 'LF'
# CR = Carriage Return = '\r', LF = Line Feed = '\n', CRLF = '\r\n', LFCR = '\n\r'
config['INTRUMENT']['panel'] = 'REAR'

config['PARAMETERS'] = {}
config['PARAMETERS']['chan_to_read'] = '101,102'
# Channels coma separated

with open('k2700config.ini','w') as configfile:
    config.write(configfile)