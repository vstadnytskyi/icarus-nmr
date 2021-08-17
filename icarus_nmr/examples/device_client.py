from caproto.threading.client import Context
ctx = Context()
ca_name = 'device_dl:'
dio,data,queue_length,packet_shape = ctx.get_pvs(f'{ca_name}dio',
    f'{ca_name}data',
    f'{ca_name}queue_length',
    f'{ca_name}packet_shape',)
