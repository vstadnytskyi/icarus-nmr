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

if sys.version_info[0] == 3:
    if sys.version_info[1] <= 7:
        from time import gmtime, strftime, time, sleep, clock
    else:
        from time import gmtime, strftime, time, sleep
        from time import perf_counter as clock
else:
    from time import gmtime, strftime, time, sleep, clock

import numpy as np

logging_shape = (1080,768, 3)
pre_shape = (216,768, 3)
depre_shape = (216,768, 3)
period_shape = (216,768, 3)
arr_shape = (64,10)

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

    arr_logging = np.zeros(logging_shape).flatten() + 255
    image_logging = pvproperty(value=arr_logging, dtype = int, max_length = logging_shape[0]*logging_shape[1]*logging_shape[2])

    arr_pre = np.zeros(pre_shape).flatten() + 255
    image_pre = pvproperty(value=arr_pre, dtype = int, max_length = pre_shape[0]*pre_shape[1]*pre_shape[2])

    arr_depre = np.zeros(depre_shape).flatten() + 255
    image_depre = pvproperty(value=arr_depre, dtype = int, max_length = depre_shape[0]*depre_shape[1]*depre_shape[2])

    arr_period = np.zeros(period_shape).flatten() + 255
    image_period = pvproperty(value=arr_period, dtype = int, max_length = period_shape[0]*period_shape[1]*period_shape[2])

    t1 = pvproperty(value=1.0)
    dt = pvproperty(value=1.0, precision = 3)

    server_name = pvproperty(value='event_handler_mock')

    sample_pressure = pvproperty(value=0.0, read_only = True, dtype = float, precision = 3)
    target_pressure = pvproperty(value=0.0, read_only = True, dtype = float, precision = 3)

    pump_counter = pvproperty(value=0)
    valves_per_pump_current = pvproperty(value=1.0, precision = 2)
    valves_per_pump_total = pvproperty(value=1.0, precision = 2)

    ctrl_operating_mode = pvproperty(value=1)
    ctrl_shutdown_state = pvproperty(value=0,dtype = int)
    ctrl_pump_state = pvproperty(value=0,dtype = int)
    ctrl_disable_pump_state = pvproperty(value=0,dtype = int)
    ctrl_pre_state = pvproperty(value=0,dtype = int)
    ctrl_depre_state = pvproperty(value=0,dtype = int)


    table_pressure_after_pre = pvproperty(value=1.0, precision = 3)
    table_pressure_before_depre = pvproperty(value=1.0, precision = 3)
    table_time_to_switch_pre = pvproperty(value=1.0, precision = 3)
    table_time_to_switch_depre = pvproperty(value=1.0, precision = 3)
    table_rise_slope = pvproperty(value=1.0, precision = 3)
    table_fall_slope = pvproperty(value=1.0, precision = 3)
    table_pulse_width_pre = pvproperty(value=1.0, precision = 3)
    table_pulse_width_depre = pvproperty(value=1.0, precision = 3)
    table_delay = pvproperty(value=1.0, precision = 3)
    table_period = pvproperty(value=1.0, precision = 3)
    table_valve_counter_pre = pvproperty(value=1.0, precision = 3)
    table_valve_counter_depre = pvproperty(value=1.0, precision = 3)

    warning_text = pvproperty(value='this is a warning/faults field')

    @sample_pressure.startup
    async def sample_pressure(self, instance, async_lib):
        # This method will be called when the server starts up.
        self.io_pull_queue = async_lib.ThreadsafeQueue()
        self.io_push_queue = async_lib.ThreadsafeQueue()
        self.device.io_push_queue = self.io_push_queue
        self.device.io_pull_queue = self.io_pull_queue


        # Loop and grab items from the response queue one at a time
        while True:
            io_dict = await self.io_push_queue.async_get()
            # Propagate the keypress to the EPICS PV, triggering any monitors
            # along the way
            for key in list(io_dict.keys()):
                if key == 'sample_pressure':
                    await self.sample_pressure.write(io_dict[key])
                elif key == 'target_pressure':
                    await self.target_pressure.write(io_dict[key])
                elif key == 'valves_per_pump_current':
                    await self.valves_per_pump_current.write(io_dict[key])
                elif key == 'valves_per_pump_total':
                        await self.valves_per_pump_total.write(io_dict[key])
                elif key == 'pump_counter':
                    await self.pump_counter.write(io_dict[key])
                elif key == 'table_pulse_width_depre':
                    await self.table_pulse_width_depre.write(io_dict[key])
                elif key == 'table_time_to_switch_depre':
                    await self.table_time_to_switch_depre.write(io_dict[key])
                elif key == 'table_fall_slope':
                    await self.table_fall_slope.write(io_dict[key])
                elif key == 'image_depre':
                    await self.image_depre.write(io_dict[key])

                elif key == 'table_time_to_switch_pre':
                    await self.table_time_to_switch_pre.write(io_dict[key])
                elif key == 'table_rise_slope':
                    await self.table_rise_slope.write(io_dict[key])
                elif key == 'image_pre':
                    await self.image_pre.write(io_dict[key])


if __name__ == '__main__':


    ioc_options, run_options = ioc_arg_parser(
        default_prefix='event_handler_mock:',
        desc=dedent(Server.__doc__))
    ioc = Server(**ioc_options)


    ioc.device = device
    run(ioc.pvdb, **run_options)
