from caproto.threading.client import Context
ctx = Context()
ca_name = 'device_dl:'
dio,dio0,dio1,dio2,dio3,dio4,dio5,dio6,data,queue_length = ctx.get_pvs(f'{ca_name}dio',
    f'{ca_name}dio0',
    f'{ca_name}dio1',
    f'{ca_name}dio2',
    f'{ca_name}dio3',
    f'{ca_name}dio4',
    f'{ca_name}dio5',
    f'{ca_name}dio6',
    f'{ca_name}data',
    f'{ca_name}queue_length',)
