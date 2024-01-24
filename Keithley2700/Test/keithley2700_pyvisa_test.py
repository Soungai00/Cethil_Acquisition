import pyvisa

rm = pyvisa.ResourceManager()       # rm class = ResourceManager

# Display resources list
print(rm.list_resources())

# Open the wanted resource
instrument = rm.open_resource('ASRL1::INSTR')

# Identification query to initiate dialog
print(instrument.query("*IDN?"))

# Set Keithley mode to temperature acquisition
instrument.write("func 'temp'")

# Display temperature (last reading without trigger)
print(instrument.query("fetch?"))

# Close resource
instrument.close()