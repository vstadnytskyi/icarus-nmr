"""
Simple code to create an instance of the device level class in a terminal, bind mock driver and initilize the device with init command.

The toggle_valves() function opens and closes depressurization and pressurization valves
"""

from icarus_nmr.device_daq import DI4108_DL
device = DI4108_DL()
from icarus_nmr.driver_mock import Driver
driver = Driver()
device.bind_driver(driver)
device.init()
from matplotlib import pyplot as plt
from time import sleep
import numpy as np
def toggle_valves():
     from time import sleep
     device.set_DIO(127-2);
     sleep(1)
     device.set_DIO(127);
     sleep(1)
     device.set_DIO(127-4)
     sleep(1)
     device.set_DIO(127)

toggle_valves()
sleep(3)
data = np.copy(device.queue.peek_all())

plt.figure()
plt.plot(data[:,5],label = 'sample pressure origin')
plt.plot(data[:,6],label = 'sample pressure destination')
plt.legend()

plt.figure()
plt.plot(data[:,0],label = 'channel 0')
plt.plot(data[:,1],label = 'channel 1')
plt.plot(data[:,2],label = 'channel 2')
plt.plot(data[:,3],label = 'channel 3')
plt.plot(data[:,4],label = 'channel 4')
plt.legend()
