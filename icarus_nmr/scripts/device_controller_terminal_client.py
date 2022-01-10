#!/usr/bin/env python3
"""

"""
import socket
device_ca_server_prefix = f'{socket.gethostname()}_device_controller:'

from caproto.threading.client import Context
ctx = Context()
ca_name = device_ca_server_prefix
pv_names = ['dio',
                'freq',
                'queue_length',
                'data',
                'peek_data',
                'packet_shape',
                'LIST']
pvs = {}
def pulse_sequence_1(current_state = 126):
    from time import time, sleep
    pvs['dio'].write(current_state-2)
    sleep(0.25)
    pvs['dio'].write(current_state)
    sleep(0.5)
    pvs['dio'].write(current_state-4)
    sleep(0.25)
    pvs['dio'].write(current_state)

def pulse_sequence_2(current_state = 126):
    from time import time, sleep
    pvs['dio'].write(current_state-4)
    sleep(0.25)
    pvs['dio'].write(current_state)
    sleep(0.5)
    pvs['dio'].write(current_state-2)
    sleep(0.25)
    pvs['dio'].write(current_state)

def run_N(N = 10):
    from time import sleep, time, ctime
    for i in range(100):
        ctime(time())
        pulse()
        sleep(8)


for item in pv_names:
    pvs[item], = ctx.get_pvs(f'{ca_name}{item}',)
if __name__ == '__main__':
    pass
