import time
import pyvisa
import py2700 as DMM

rm = pyvisa.ResourceManager()       # rm class = ResourceManager

# Display resources list
print(rm.list_resources())

# Select our resource
#instrK2700 = DMM.Multimeter('ASRL1::INSTR')
instrK2700 = DMM.Multimeter(rm.list_resources()[0])         # When our instrument is the first (or only) resource

print(instrK2700.query('*IDN?'))

# Set the default temperature units
instrK2700.set_temperature_units('C')

# Set Channels 101, 102 as K-type thermocouples with internal cold junction
instrK2700.define_channels([101,102],
    DMM.MeasurementType.thermocouple('K','INT'))

# Setup for reading:
#   This needs to be completed after channel definitions and before scanning
instrK2700.setup_scan()


# Scan the channels, given the timestamp you want for the reading
i = 0
numPoints = 10 

while i < numPoints :
    result = instrK2700.scan(time.time_ns()/(10**9))
    print(result)
    i+=1

# Disconnect
instrK2700.disconnect()