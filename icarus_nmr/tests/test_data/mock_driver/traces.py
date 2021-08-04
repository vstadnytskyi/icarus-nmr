from icarus_nmr.tests.test_data.mock_driver import traces
import os
head, tail = os.path.split(traces.__file__)
print(head, tail )
def get_lst_pre_trace(N = None):
    import os
    head, tail = os.path.split(traces.__file__)
    from ubcs_auxiliary.save_load_object import load_from_file as load
    lst = []
    for item in os.listdir(head):
        if '_pre.' in item:
            lst.append(load(os.path.join(head,item)))
    return lst

def get_lst_depre_trace(N = None):
    import os
    head, tail = os.path.split(traces.__file__)
    from ubcs_auxiliary.save_load_object import load_from_file as load
    lst = []
    for item in os.listdir(head):
        if '_depre.' in item:
            lst.append(load(os.path.join(head,item)))
    return lst

def get_lst_pump_trace(N = None):
    import os
    head, tail = os.path.split(traces.__file__)
    from ubcs_auxiliary.save_load_object import load_from_file as load
    lst = []
    for item in os.listdir(head):

        if '_pump.' in item:
            lst.append(load(os.path.join(head,item)))
    return lst
