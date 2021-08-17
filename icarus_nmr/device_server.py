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
from time import time, sleep, ctime

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

    freq = pvproperty(value=4000.0, read_only = True, dtype = float, precision = 1)
    dio = pvproperty(value=0, read_only = False, dtype = int)


    queue_length = pvproperty(value=0, read_only = True, dtype = int)
    data = pvproperty(value=zeros(shape = (64*10,)), read_only = True, dtype = int, max_length = 40000000)
    peek_data = pvproperty(value=zeros(shape = (6400*10,)), read_only = True, dtype = int, max_length = 40000000)
    packet_shape = pvproperty(value=arr_shape, read_only = True, dtype = int)
    LIST = pvproperty(value=[0.0,0.0,0.0,0.0])



    @freq.startup
    async def freq(self, instance, async_lib):
        # This method will be called when the server starts up.
        self.io_pull_queue = async_lib.ThreadsafeQueue()
        self.io_push_queue = async_lib.ThreadsafeQueue()
        self.device.io_push_queue = self.io_push_queue
        self.device.io_pull_queue = self.io_pull_queue

        await self.freq.write(self.device.pr_rate)




        # Loop and grab items from the response queue one at a time
        while True:
            io_dict = await self.io_push_queue.async_get()
            # Propagate the keypress to the EPICS PV, triggering any monitors
            # along the way
            print(f'inside while True {io_dict}')
            for key in list(io_dict.keys()):
                if key == 'dio':
                    await self.dio.write(io_dict[key])

                elif key == 'a':
                    await self.a.write(io_dict[key])
                elif key == 'b':
                    await self.b.write(io_dict[key])
                elif key == 'c':
                    await self.c.write(io_dict[key])
                elif key == 'd':
                    await self.d.write(io_dict[key])

    @dio.startup
    async def dio(self, instance, async_lib):
        await self.dio.write(self.device.DIO)
    @dio.putter
    async def dio(self, instance, value):
        print('Received update for the {}, sending new value {}'.format('dio',value))
        self.device.set_DIO(value = value)
        return value
    @dio.getter
    async def dio(self, instance):
        print(f"getter: {'dio'}, new value ")
        value = self.device.get_DIO()
        return value

    @data.getter
    async def data(self, instance):
        value = self.device.queue.dequeue(self.device.pr_packet_size).flatten()
        if value.shape[0] > 1280:
            print(f'{value.shape}')
            print(f"getter: {'data'}, queue length {self.device.queue.length}")
            print(f"getter: {'data'}, queue rear {self.device.queue.rear}")
        return value

    @peek_data.getter
    async def peek_data(self, instance):
        value = self.device.queue.peek_first_N(N=6400).flatten()
        return value

    @queue_length.startup
    async def queue_length(self, instance, async_lib):
        await self.queue_length.write(self.device.queue.length)
    @queue_length.getter
    async def queue_length(self, instance):
        print(f"getter: {'data'}, queue length {self.device.queue.length}")
        value = self.device.queue.length
        return value

    # @ai_offset.startup
    # async def ai_offset(self, instance, async_lib):
    #     await self.ai_offset.write(self.device.pressure_sensor_offset)
    # @ai_offset.putter
    # async def ai_offset(self, instance, value):
    #     print(f"Received update for the {'dio'}, sending new value {value}")
    #     self.device.pressure_sensor_offset = value
    #     return value
    # @ai_offset.getter
    # async def ai_offset(self, instance):
    #     print(f"getter: {'ai_offset'}, new value ")
    #     value = self.device.pressure_sensor_offset
    #     return value


if __name__ == '__main__':
    from icarus_nmr.device_daq import DI4108_DL
    device = DI4108_DL()
    device.pr_buffer_size =  (6400,10)
    from icarus_nmr.mock_driver import Driver
    driver = Driver()
    device.bind_driver(driver)
    device.init()

    ioc_options, run_options = ioc_arg_parser(
        default_prefix='device_dl:',
        desc=dedent(Server.__doc__))
    ioc = Server(**ioc_options)
    device.pr_pracket_size = 128

    ioc.device = device
    run(ioc.pvdb, **run_options)
