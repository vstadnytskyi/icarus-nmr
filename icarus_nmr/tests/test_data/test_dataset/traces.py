from icarus_nmr.tests.test_data.test_dataset import traces
import os
head, tail = os.path.split(traces.__file__)
head += '/buffer_files'
print(head, tail )
def get_lst_pre_trace(N = None):
    import os
    from numpy import loadtxt
    head, tail = os.path.split(traces.__file__)
    head += '/buffer_files'
    from ubcs_auxiliary.save_load_object import load_from_file as load
    lst = []
    for item in os.listdir(head):
        if '_pre.' in item:
            data = loadtxt(os.path.join(head,item), delimiter = ',')
            lst.append(data)
    return lst

def get_lst_depre_trace(N = None):
    import os
    from numpy import loadtxt
    head, tail = os.path.split(traces.__file__)
    head += '/buffer_files'
    from ubcs_auxiliary.save_load_object import load_from_file as load
    lst = []
    for item in os.listdir(head):
        if '_depre.' in item:
            data = loadtxt(os.path.join(head,item), delimiter = ',')
            lst.append(data)
    return lst

def get_lst_pump_trace(N = None):
    import os
    from numpy import loadtxt
    head, tail = os.path.split(traces.__file__)
    head += '/buffer_files'
    from ubcs_auxiliary.save_load_object import load_from_file as load
    lst = []
    for item in os.listdir(head):

        if '_pump.' in item:
            data = loadtxt(os.path.join(head,item), delimiter = ',')
            lst.append(data)
    return lst
