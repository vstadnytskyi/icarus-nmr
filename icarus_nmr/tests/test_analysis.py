import unittest
import os

thisdir, thisfile = os.path.split(__file__)
root = os.path.join(thisdir, 'test_data','test_dataset/')

class QueueTest(unittest.TestCase):

    def test_log_read_file(self):
        "Check that one and one are indeed two."
        from os import getcwd
        print(getcwd())

    def test_log_read_file(self):
        "Check that one and one are indeed two."
        from icarus_nmr import analysis
        folder = root
        dataset = analysis.Dataset(folder)
        raw_data, data = dataset.log_read_file(folder = folder)
        self.assertEqual(raw_data.shape, (980, 37))
        self.assertEqual(data.shape, (403, 37))

    def test_log_read_header(self):
        from icarus_nmr import analysis
        folder = root
        dataset = analysis.Dataset(folder)
        header = dataset.log_read_header(folder)
        lst = ['time',
                 'global_pointer',
                 'period_idx',
                 'event_code',
                 'pPre_0',
                 'pDepre_0',
                 'pPre_after_0',
                 'pDiff_0',
                 'tSwitchDepressure_0',
                 'tSwitchDepressureEst_0',
                 'tSwitchPressure_0',
                 'tSwitchPressureEst_0',
                 'gradientPressure_0',
                 'gradientDepressure_0',
                 'gradientPressureEst_0',
                 'gradientDepressureEst_0',
                 'riseTime_0',
                 'fallTime_0',
                 'pPre_1',
                 'pDepre_1',
                 'pPre_after_1',
                 'pDiff_1',
                 'tSwitchDepressure_1',
                 'tSwitchPressure_1',
                 'gradientPressure_1',
                 'gradientDepressure_1',
                 'fallTime_1',
                 'riseTime_1',
                 'period',
                 'delay',
                 'pressure_pulse_width',
                 'depressure_pulse_width',
                 'pump_stroke',
                 'depressure_valve_counter',
                 'pressure_valve_counter',
                 'leak_value',
                 'meanbit3']
        self.assertEqual(header, lst)
