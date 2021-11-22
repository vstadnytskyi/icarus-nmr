#!/usr/bin/env python3
"""

"""
from pdb import pm



if __name__ is "__main__":
    from icarus_nmr.event_handler import Handler
    from icarus_nmr.event_daq import DAQ
    from icarus_nmr.event_client import Client
    from icarus_nmr.event_server import Server

    import socket

    SERVER_NAME = socket.gethostname()
    client = Client(device_ca_server_prefix = f'device_{SERVER_NAME}:',dio_ca_server_prefix = f'dio_{SERVER_NAME}:')

    daq = DAQ(client)
    daq.init()

    from time import sleep

    for i in range(100):
        daq.run_once()

    handler = Handler(daq)
    handler.init()
    handler.fault_detection_init()

    self = handler

    for i in range(2000):
        daq.run_once(); handler.run_once_once();
        if len(self.events_list)>0:
            print(self.events_list); self.evaluate_events();

    from tempfile import gettempdir
    import logging
    logging.basicConfig(filename=gettempdir()+'/icarus_event_controller_debug.log',
                        level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
