import unittest
from numpy.testing import assert_array_equal
import sys
if sys.version_info[0] < 3:
    from time import clock
else:
    from time import perf_counter as clock

class MockTest(unittest.TestCase):
    def test_init_device(self):
        from ..mock_driver import Driver
        from ..device import DI4108_DL
        from time import sleep
        driver = Driver()
        device = DI4108_DL()
        device.init(driver = driver)
        device.start()
        dic = {b'Device name': '4108',
                 b'Firmware version': 'VS',
                 b'Serial Number': '00000000',
                 b'Sample Rate Divisor': '60000000'}
        result = device.driver.get_hardware_information()
        self.assertEqual(dic,result)
        result = driver.get_hardware_information()
        self.assertEqual(dic,result)
        sleep(0.05)
        length1 = device.queue.length
        data,flag = device.driver.get_readings(length1)
        self.assertEqual(data.T[9].mean(),127.0)
        self.assertEqual(data.T[9].std(), 0.0)
        self.assertEqual(length1, 128)
