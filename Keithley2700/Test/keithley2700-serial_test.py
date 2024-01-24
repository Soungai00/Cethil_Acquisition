import time
import serial



# configure the serial connections (the parameters differs on the device you are connecting to)
ser = serial.Serial(
    port='COM1',
    baudrate=9600,
    timeout=1,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
)
ser.isOpen()

# Reading the data from the serial port.
# Test of *IDN? query
# Expected answer : KEITHLEY INSTRUMENTS INC.,MODEL 2700,1233731,B09  /A02  


# get keyboard input
bytesToRead = ser.inWaiting()
data = ser.read(bytesToRead)
time.sleep(1)
print(data)

ser.write('*IDN?'.encode('utf-8'))