from ubcs_auxiliary.XLI.client import Client_LL
client = Client_LL()
device = {}
device[b'icarus-0'] = {b'ip_address':'127.0.0.1',b'port':2030}

i=client.indicators(device = device[b'icarus-0'], indicators = {b'all':None});
c=client.controls(device = device[b'icarus-0'], controls = {b'all':None});
inds_list = {}
ctrls_list = {}
inds_list = i[b'message'][b'indicators']
ctrls_list = c[b'message'][b'controls']
