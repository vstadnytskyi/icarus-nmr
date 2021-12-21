import unittest
from numpy.testing import assert_array_equal
import sys
import os
import numpy as np
if sys.version_info[0] < 3:
    from time import clock
else:
    from time import perf_counter as clock
thisdir, thisfile = os.path.split(__file__)
root = os.path.join(thisdir, 'test_data','test_dataset/buffer_files')

class EventHandlerTest(unittest.TestCase):
    def test_find_dio_events(self):
        filename = os.path.join(root,'1564501925.7699604_0_pre.csv')
        data = np.loadtxt(filename, delimiter = ',')
        from icarus_nmr.event_handler import Handler
        handler = Handler(daq = None)
        res_lst = handler.find_dio_events(data,circular_packet_pointer=0,linear_packet_pointer=0,packet_length=480)
        test_lst = [{b'channel': 'D2',
                      b'value': 'low',
                      b'index': 79,
                      b'global_index': 79,
                      b'evt_code': 20},
                     {b'channel': 'period', b'index': 79, b'global_index': 79, b'evt_code': 200}]
        self.assertEqual(res_lst, test_lst)

        res_lst = handler.find_dio_events(data[:100],circular_packet_pointer=0,linear_packet_pointer=0,packet_length=100)
        test_lst = [{b'channel': 'D2',
                      b'value': 'low',
                      b'index': 79,
                      b'global_index': 79,
                      b'evt_code': 20},
                     {b'channel': 'period', b'index': 79, b'global_index': 79, b'evt_code': 200}]
        self.assertEqual(res_lst, test_lst)
