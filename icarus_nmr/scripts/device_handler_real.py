#!/usr/bin/env python3
"""
DATAQ 4108 Device Level code
author: Valentyn Stadnytskyi
Date: November 2017 - August 2021

This is an example script that starts "mock" device channel access server.

The variable SERVER_NAME needs to be changed to launch the server with a unique name that corresponds to the desired server.


"""
from caproto.server import pvproperty, PVGroup, ioc_arg_parser, run
from textwrap import dedent
from pdb import pm

from numpy import random, array, zeros, ndarray, nan, isnan
from time import time,sleep

import socket

SERVER_NAME = socket.gethostname()

if __name__ == '__main__':


    from caproto.server import pvproperty, PVGroup, ioc_arg_parser, run
    import caproto
    from textwrap import dedent
    from pdb import pm




    from numpy import random, array, zeros, ndarray, nan, isnan
    from time import time, sleep

    # import device (DI_4108_DL) class and initiate device instance.
    from icarus_nmr.device_daq import Device
    device = Device()

    #########
    # the driver binding section needs to be changed when using actual physical device instead of a mock device
    from icarus_nmr.driver_usb_bulk_di_4108 import Driver
    driver = Driver()
    device.bind_driver(driver)
    #########


    device.init()
    device.start()

    from icarus_nmr.device_server import Server

    ioc_options, run_options = ioc_arg_parser(
        default_prefix=f'device_{SERVER_NAME}:',
        desc=dedent(Server.__doc__))
    ioc = Server(**ioc_options)

    # the device instance is shared with ioc.device instance which allows two moduled to talk to each other.
    ioc.device = device
    run(ioc.pvdb, **run_options)
