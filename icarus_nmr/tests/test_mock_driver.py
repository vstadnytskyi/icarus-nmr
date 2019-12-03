import unittest
from numpy.testing import assert_array_equal

class MockTest(unittest.TestCase):
    def test_get_hardware_information(self):
        from ..mock_driver import Driver
        driver = Driver()
        driver.init()
        dic = {b'Device name': '4108',
                 b'Firmware version': 'VS',
                 b'Serial Number': '00000000',
                 b'Sample Rate Divisor': '60000000'}
        result = driver.get_hardware_information()
        self.assertEqual(dic,result)

    def test_configure(self):
        from ..mock_driver import Driver
        driver = Driver()
        driver.init()
        driver.set_acquisition_rate(dec = 5)
        self.assertEqual(driver.sim_rate,4000)
        driver.set_acquisition_rate(dec = 4)
        self.assertEqual(driver.sim_rate,5000)

    def test_inquire(self):
        from ..mock_driver import Driver
        driver = Driver()
        driver.init()
        reply = driver.inquire('info 1 \r')
        self.assertEqual('info 1  4108\r',reply)
        reply = driver.inquire('info 5 \r')
        self.assertEqual('info 5  Mary_Smith\r',reply)

    def test_start_stop_scan(self):
        from ..mock_driver import Driver
        driver = Driver()
        driver.init()
        self.assertEqual(driver.sim_flag,False)
        driver.start_scan()
        self.assertEqual(driver.sim_flag,True)
        driver.stop_scan()
        self.assertEqual(driver.sim_flag,False)

    def test_get_readings(self):
        from ..mock_driver import Driver
        driver = Driver()
        driver.init()
        driver.start_scan()
        data, flag = driver.get_readings(512)
        self.assertEqual(data.shape,(10,512))
        self.assertEqual(data[9].mean(),127.0)
        self.assertEqual(data[9].std(), 0.0)

    def test_set_digital(self):
        from ..mock_driver import Driver
        driver = Driver()
        driver.init()
        driver.start_scan()
        data, flag = driver.get_readings(512)
        self.assertEqual(data[9].mean(),127.0)

        driver.set_digital(126)
        data, flag = driver.get_readings(512)
        self.assertEqual(data[9].mean(),126.0)

        driver.set_digital(122)
        data, flag = driver.get_readings(512)
        self.assertEqual(data[9].mean(),122.0)


    def test_get_pre_trace(self):
        from ..mock_driver import Driver
        driver = Driver()
        driver.init()
        driver.start_scan()
        trace = driver.get_pre_trace()
        self.assertEqual(trace.shape,(10, 333))
        self.assertEqual(trace[5,0] < 6000.0,True)
        self.assertEqual(trace[5,-1] < 6000.0,False)


    # def test_1(self):
    #     from numpy import random
    #     from ..circular_buffer import CircularBuffer
    #     buffer = CircularBuffer(shape=(100, 2, 4))
    #     data = random.randint(1024, size=(5, 2, 4))
    #     buffer.packet_length = 5
    #     buffer.append(data)
    #     self.assertEqual(buffer.pointer, 4)
    #     self.assertEqual(buffer.g_pointer, 4)
    #     self.assertEqual(buffer.packet_pointer, 0)
    #     self.assertEqual(buffer.g_packet_pointer, 0)
    # def test_queue_end(self):
    #     """
    #     test if the default pointer in the buffer is -1.
    #     """
    #     from ..circular_buffer import CircularBuffer
    #     buffer = CircularBuffer(shape=(100, 2))
    #     self.assertEqual(buffer.pointer, -1)
    #
    # def test_queue_end_two(self):
    #     """
    #     test if the default pointer in the buffer is -1.
    #     """
    #     from ..circular_buffer import CircularBuffer
    #     buffer = CircularBuffer(shape=(100, 2))
    #     self.assertEqual(buffer.pointer, -1)
    #
    # def test_1(self):
    #     from numpy import random
    #     from ..circular_buffer import CircularBuffer
    #     buffer = CircularBuffer(shape=(100, 2, 4))
    #     data = random.randint(1024, size=(5, 2, 4))
    #     buffer.packet_length = 5
    #     buffer.append(data)
    #     self.assertEqual(buffer.pointer, 4)
    #     self.assertEqual(buffer.g_pointer, 4)
    #     self.assertEqual(buffer.packet_pointer, 0)
    #     self.assertEqual(buffer.g_packet_pointer, 0)
    #
    # def test_attributes(self):
    #     from ..circular_buffer import CircularBuffer
    #     from numpy import random
    #     buffer = CircularBuffer(shape=(100, 2), dtype='int16')
    #     data = random.randint(1024, size=(5, 2))
    #     buffer.append(data)
    #     self.assertEqual(buffer.shape, (100, 2))
    #     self.assertEqual(buffer.size, 100*2)
    #     self.assertEqual(buffer.dtype, 'int16')
    #
    # def test_full(self):
    #     from ..circular_buffer import CircularBuffer
    #     from numpy import random, sum
    #     buffer = CircularBuffer(shape=(100, 2, 3), dtype='float64')
    #     data = random.randint(1024, size=(50, 2, 3))
    #     buffer.append(data)
    #     assert buffer.pointer == 49
    #     assert buffer.g_pointer == 49
    #     assert buffer.shape == (100, 2, 3)
    #     assert buffer.size == buffer.buffer.shape[0]*buffer.buffer.shape[1]*buffer.buffer.shape[2]
    #     assert buffer.dtype == 'float64'
    #     assert sum(buffer.get_i_j(i=5, j=6)) == sum(buffer.buffer[5])
    #     # get data between pointers 5 and 10 and compare to get 5 points from pointer M
    #     assert sum(buffer.get_i_j(i=5, j=10)) == sum(buffer.get_N(N=5, M=9))
