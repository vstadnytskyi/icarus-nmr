#from icarus_SL import icarus_SL#!/bin/env python
"""
The Event Detector LL for the High Pressure Apparatus
author: Valentyn Stadnytskyi
dates: June 09 2018 - November 16 2018

1.0.0 - the improved copy from the old class from the older SL
1.1.0 - Bugs fixed and Fully tested version that works with SL server! Exciting
      - EvalEvent function was changed. The list is cleared at the end of analysis.

Events:
two numbers: first D channel number and second direction 0(down) and 1(up)
00 - D0 goes low
01 - D0 goes high
10 - D1 goes low
11 - D1 goes high
20 - D2 goes low
21 - D2 goes high
and so on

3 digital numbers starting with 100 are analog events:
100 - analog event of high pressure pump stroke

version 3.0.0 - added tube_length and medium
 - 4.0.0 - majopr upgrade to Python 3 and minor restructuring

"""
__version__ = '4.0.0' #
import sys

import traceback

import sys
if sys.version_info[0] == 3:
    if sys.version_info[1] <= 7:
        from time import gmtime, strftime, time, sleep, clock
    else:
        from time import gmtime, strftime, time, sleep
        from time import perf_counter as clock
else:
    from time import gmtime, strftime, time, sleep, clock

from logging import debug,info,warn,error
from numpy import nan, std, inf, nanmean, nanstd, nonzero, zeros, nanargmax, nanargmin, nanmin, nanmax, asarray
import platform
import pickle
import traceback
import scipy.stats
from scipy.interpolate import UnivariateSpline

from pdb import pm

class Client():
    def __init__(self,device_ca_server_prefix = 'device_mock:', dio_ca_server_prefix = 'digital_handler_mock:'):
        """
        ToDo: rewrite the function to include the list of PVs.
        - restructure subscription to PVs to be saved as a dictionary. this will allow potential future expansions.
        """
        from caproto.threading.client import Context
        self.ctx = Context()
        self.ca_name = device_ca_server_prefix
        self.dio_ca_name = dio_ca_server_prefix
        self.dio,self.dio_device,self.data,self.peek_data,self.queue_length,self.packet_shape,self.freq = self.ctx.get_pvs(f'{self.dio_ca_name}dio',
            f'{self.ca_name}dio',
            f'{self.ca_name}data',
            f'{self.ca_name}peek_data',
            f'{self.ca_name}queue_length',
            f'{self.ca_name}packet_shape',
            f'{self.ca_name}freq',)

    def get_dio(self):
        return self.dio.read().data[0]
    def set_dio(self, value):
        self.dio.write(value)

if __name__ == "__main__":
    from importlib import reload
    from tempfile import gettempdir
    import logging
    import matplotlib
    matplotlib.use('WxAgg')
    client = Client()
    daq = DAQ(client)
    daq.init()
    event_detector = Event_Detector()
    logging.basicConfig(filename=gettempdir()+'/di4108_DL.log',
                        level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

    event_detector.init()
    from numpy import array
    self = event_detector
    temp_lst = {b'tSwitchPressure_0':1,b'tSwitchPressure_1':2,b'tSwitchPressureEst_0':3,b'gradientPressure_0':4,b'gradientPressure_1':5,b'gradientPressureEst_0':6}
