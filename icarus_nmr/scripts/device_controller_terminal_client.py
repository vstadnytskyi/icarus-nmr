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
for item in pv_names:
    pvs[item], = ctx.get_pvs(f'{ca_name}{item}',)
if __name__ == '__main__':
    pass
