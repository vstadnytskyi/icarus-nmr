#!/usr/bin/env python3
"""
DATAQ 4108 Device Level code
author: Valentyn Stadnytskyi
Date: November 2017- April 2019

fully python3 compatible.

The main purpose of this module is to provide useful interface between DI-4108 and a server system level code that does all numbercrynching. This modules only job is to attend DI-4108 and insure that all data is collected and stored in a circular buffer.



"""
from caproto.server import pvproperty, PVGroup, ioc_arg_parser, run
import caproto
from textwrap import dedent
from pdb import pm

from numpy import random, array, zeros, ndarray, nan, isnan
from time import time,sleep

if __name__ == '__main__':
    from caproto.server import pvproperty, PVGroup, ioc_arg_parser, run
    import caproto
    from textwrap import dedent
    from pdb import pm

    from numpy import random, array, zeros, ndarray, nan, isnan
    from time import time, sleep

    from icarus_nmr.dio_server import Server
    from icarus_nmr.dio_client import Client
    from icarus_nmr.dio_handler import Handler

    import socket
    client = Client(device_ca_server_prefix = f'device_{socket.gethostname()}:')
    device = Handler(client)

    ioc_options, run_options = ioc_arg_parser(
        default_prefix=f'digital_handler_{socket.gethostname()}:',
        desc=dedent(Server.__doc__))
    ioc = Server(**ioc_options)
    ioc.device = device
    run(ioc.pvdb, **run_options)
