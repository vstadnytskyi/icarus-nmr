#!/usr/bin/env python3
"""

"""
from pdb import pm

from icarus_nmr.event_handler import Handler
from icarus_nmr.event_daq import DAQ
from icarus_nmr.event_client import Client

client = Client()
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
