"""
DATAQ 4108 Device Level code
author: Valentyn Stadnytskyi
Date: November 2017- April 2019

fully python3 compatible.

The main purpose of this module is to provide useful interface between DI-4108 and a server system level code that does all numbercrynching. This modules only job is to attend DI-4108 and insure that all data is collected and stored in a circular buffer.

The communication in this module is done via XLI module developed by Valentyn Stadnytskyi. This module is based on python sockets.

"""#!/usr/bin/env python3
"""
Simple IOC based on caproto library.
It has
"""
from caproto.server import pvproperty, PVGroup, ioc_arg_parser, run
import caproto
from textwrap import dedent
from pdb import pm

from numpy import random, array, zeros, ndarray, nan, isnan

import sys
if sys.version_info[0] == 3:
    if sys.version_info[1] <= 7:
        from time import gmtime, strftime, time, sleep, clock, ctime
    else:
        from time import gmtime, strftime, time, sleep, ctime
        from time import perf_counter as clock
else:
    from time import gmtime, strftime, time, sleep, clock, ctime

import numpy as np

class Server(PVGroup):
    """
    An IOC with three uncoupled read/writable PVs

    Scalar PVs
    ----------
    CPU
    MEMORY
    BATTERY

    Vectors PVs
    -----------

    """
    running = pvproperty(value=1)

    array_shape = [1080,600,3]
    array1 = np.zeros(array_shape).flatten() + 128
    shape1 = pvproperty(value=array_shape)
    image1 = pvproperty(value=array1, dtype = int, max_length = array_shape[0]*array_shape[1]*array_shape[2])

    button1 = pvproperty(value=0, dtype = bool)
    button1_enable = pvproperty(value=1, dtype = bool)

    toggle_button1 = pvproperty(value=0, dtype = bool)
    toggle_button1_enable = pvproperty(value=1, dtype = bool)

    @running.startup
    async def running(self, instance, async_lib):
        # This method will be called when the server starts up.
        self.io_pull_queue = async_lib.ThreadsafeQueue()
        self.io_push_queue = async_lib.ThreadsafeQueue()
        if device is not None:
            self.device.io_push_queue = self.io_push_queue
            self.device.io_pull_queue = self.io_pull_queue


        # Loop and grab items from the response queue one at a time
        while True:
            io_dict = await self.io_push_queue.async_get()
            # Propagate the keypress to the EPICS PV, triggering any monitors
            # along the way
            for key in list(io_dict.keys()):
                if key == 'button1':
                    await self.button1.write(io_dict[key])

    @button1.putter
    async def button1(self, instance, value):
        print({ctime(time())},'Received update for the {}, sending new value {}'.format('button1',value))
        #self.device.set_bit1(value)
        return value
    @button1_enable.putter
    async def button1_enable(self, instance, value):
        print(f'{ctime(time())} Received update for the {"bio1_enable"}, sending new value {value}')
        #self.device.set_DIO(value = value)
        return value

    @toggle_button1.putter
    async def toggle_button1(self, instance, value):
        print({ctime(time())},'Received update for the {}, sending new value {}'.format('toggle_button1',value))
        #self.device.set_bit1(value)
        return value
    @toggle_button1_enable.putter
    async def toggle_button1_enable(self, instance, value):
        print(f'{ctime(time())} Received update for the {"toggle_button1_enable"}, sending new value {value}')
        #self.device.set_DIO(value = value)
        return value


if __name__ == '__main__':


    ioc_options, run_options = ioc_arg_parser(
        default_prefix='pyepics_prototyping:',
        desc=dedent(Server.__doc__))
    ioc = Server(**ioc_options)

    device = None
    ioc.device = device
    run(ioc.pvdb, **run_options)
