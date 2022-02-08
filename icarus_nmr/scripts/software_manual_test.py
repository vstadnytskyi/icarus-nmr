
"""
"""
lst = ['numpy',
        'serial',
        'usb',
        'matplotlib',
        'circular_buffer_numpy',
        'ubcs_auxiliary',
        'epics',
        'scipy',
        'psutil',
        'caproto']

for item in lst:
    print('---------')
    print(f"{item} version")
    try:
        exec(f'import {item}')
        string = globals()[item].__version__
        print(f'{string}')
    except:
        print(f'ModuleNotFoundError: No module named {item}')
print('--------- --------- --------- ---------')
print('testing access to Device Controller')
print('--------- --------- --------- ---------')
from icarus_nmr import device_client
import socket
device_ca_server_prefix = f'{socket.gethostname()}_device_controller:'
dev_client = device_client.Client(device_ca_server_prefix)

dev_result = dev_client.get_all()
print(f'PVs read {dev_result.keys()}')

print('--------- --------- --------- ---------')
print('testing access to Digital Controller')
print('--------- --------- --------- ---------')


import socket
device_ca_server_prefix = f'{socket.gethostname()}_dio_controller:'

from caproto.threading.client import Context
ctx = Context()
ca_name = device_ca_server_prefix
pv_names = ['dio',
                'bit0_indicator',
                'bit0',
                'bit0_enable',
                'bit1_indicator',
                'bit1',
                'bit1_enable',
                'bit2_indicator',
                'bit2',
                'bit2_enable',
                'bit3_indicator',
                'bit3',
                'bit3_enable',
                'shutdown_state',
                'operating_mode',
                'pulse_generator_depre_width',
                'pulse_generator_pre_width',
                'pulse_generator_delay',
                'pulse_generator_period']
pvs = {}
for item in pv_names:
    pvs[item], = ctx.get_pvs(f'{ca_name}{item}',)

print(f'PVs read {pvs.keys()}')
