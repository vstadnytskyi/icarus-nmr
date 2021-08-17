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

if __name__ == '__main__':
    from icarus_nmr.device_server import Server
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
