
def find_dio_events(repeat = 10, number = 10000):
    print('------------')
    print(f'Running timeit on {find_dio_events.__name__}')
    import timeit
    import numpy as np
    import_module = "import numpy as np \n"
    import_module += "import os\n"
    import_module += "from icarus_nmr.event_handler import Handler \n"
    import_module += "handler = Handler(daq = None)  \n"
    import_module += "thisdir = os.getcwd()\n"
    import_module += "root = os.path.join(thisdir ,'icarus_nmr/tests/test_data/test_dataset/buffer_files')\n"
    import_module += "filename = os.path.join(root,'1564501925.7699604_0_pre.csv')\n"
    import_module += "data = np.loadtxt(filename, delimiter = ',')\n"

    testcode = "lst= handler.find_dio_events(data,circular_packet_pointer=0,linear_packet_pointer=0,packet_length=480)"
    lst = timeit.repeat(stmt=testcode, setup=import_module, repeat=repeat, number = number)
    arr = np.asarray(lst)
    print(f'mean = {arr.mean()/number}, stdev = {arr.std()/number}, N = {repeat*number}')
    print('------------')


if __name__ == "__main__":
    find_dio_events()
