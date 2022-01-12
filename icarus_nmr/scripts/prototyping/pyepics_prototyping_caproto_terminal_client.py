import socket
device_ca_server_prefix = f'pyepics_prototyping:'

from caproto.threading.client import Context
ctx = Context()
ca_name = device_ca_server_prefix
pv_names = ['button1',
                'toggle_button1']
pvs = {}

for item in pv_names:
    pvs[item], = ctx.get_pvs(f'{ca_name}{item}',)
