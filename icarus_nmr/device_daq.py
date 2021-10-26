"""
DATAQ 4108 Device Level code
author: Valentyn Stadnytskyi
Date: November 2017- November 2019

fully python3 compatible.

The main purpose of this module is to provide useful interface between DI-4108 and a server system level code that does all numbercrynching. This modules only job is to attend DI-4108 and insure that all data is collected and stored in a circular buffer.

The communication in this module is done via XLI module developed by Valentyn Stadnytskyi. This module is based on python sockets.

"""

import traceback
import psutil, os


from numpy import nan, mean, std, nanstd, asfarray, asarray, hstack, array, concatenate, delete, round, vstack, hstack, zeros, transpose, split, unique, nonzero, take, savetxt, min, max
import sys

if sys.version_info[0] == 3:
    if sys.version_info[1] <= 7:
        from time import gmtime, strftime, time, sleep, clock
    else:
        from time import gmtime, strftime, time, sleep
        from time import perf_counter as clock
else:
    from time import gmtime, strftime, time, sleep, clock

import os.path
import struct
from pdb import pm

from logging import debug,info,warning,error

from timeit import Timer, timeit
from circular_buffer_numpy.queue import Queue
from datetime import datetime

from ubcs_auxiliary.saved_property import DataBase, SavedProperty
from ubcs_auxiliary.threading import new_thread
from ubcs_auxiliary.advsleep import precision_sleep #home-made module for accurate sleep


class Device():
    db = DataBase(root = 'TEMP', name = 'DI4108_DL')
    #: serial number, five character long string
    pr_serial_number = SavedProperty(db,'Serial Number', '00000').init()
    pr_AI_channels = SavedProperty(db,'Number of AI',8).init()
    pr_DI_channels = SavedProperty(db,'Number of DI',1).init()
    pr_rate = SavedProperty(db,'rate(Hz)', 4000).init()
    pr_baserate = SavedProperty(db,'baserate(Hz)', 20000).init()
    pr_dec = SavedProperty(db,'dec', 5).init()
    pr_DOI_config = SavedProperty(db,'DIO config', '1111111').init()
    pr_DOI_set = SavedProperty(db,'DIO set', '1111111').init()
    pr_packet_size = SavedProperty(db,'packet size', 64).init()
    pr_packet_buffer_size = SavedProperty(db,'pr_packet_buffer_size', 1000).init()
    pr_os_buffer = SavedProperty(db,'os_buffer', 12800).init()
    pressure_sensor_offset = SavedProperty(db,'pressure_sensor_offset',
                                               [69.5595, 65.562, 68.881375, 84.2195, 86.96075, 17.248, 17.322, 0]).init() # value read at atmoshperic pressure
    pg_period = SavedProperty(db,'pg_period', 5.0).init()
    pg_pre_pulse_width = SavedProperty(db,'pg_pre_pulse_width', 0.1).init()
    pg_depre_pulse_width = SavedProperty(db,'pg_depre_pulse_width', 0.1).init()
    pg_delay_width = SavedProperty(db,'pg_delay_width', 0.5).init()
    trigger_mode = 0
    DIO_default = 126



    def __init__(self):
        self.name = 'DI4108_DL'
        self.device_info = {}
        self.device_info['empty'] = 'empty'
        self.task_name_dict = {}
        self.task_name_dict['empty'] = 'empty'
        self.pr_rate = (self.pr_baserate)/self.pr_dec
        self.pr_buffer_size = (int(self.pr_packet_size*self.pr_rate),10)
        self.queue = Queue(shape = self.pr_buffer_size, dtype = 'int16')
        self.OverflowFlag = False

        self.io_push_queue = None
        self.io_put_queue = None

        self.curr_dio = 127
        self.user_set_dio = self.curr_dio

        self.threads = {}

    def first_time_setup(self):
        """
        set control variables to factory settings
        """
        self.pr_AI_channels = 8
        self.pr_DI_channels = 1
        self.pr_packet_size = 128
        self.pr_baserate = 20000
        self.pr_dec = 5
        self.pr_rate = self.pr_baserate*1.0/self.pr_dec
        self.pr_DOI_config = '1111111' #all outputs
        self.pr_DOI_set = '1111111' #all high
        self.pressure_sensor_offset = [69.5595, 65.562, 68.881375, 84.2195, 86.96075, 17.248, 17.322, 0]

    def bind_driver(self, driver = None):
        """
        bind driver to device instance
        """
        self.driver = driver

    def _init(self):
        if self.driver is not None:
            self.driver.init()
            self.device_info = {**self.driver.get_hardware_information(),**self.device_info}
            self.stop()
            self.config_DL(baserate = self.pr_baserate,dec = self.pr_dec, DOI_config = self.pr_DOI_config, DOI_set = self.pr_DOI_set)
        else:
            warning('The driver object in the device _init() is {}'.format(driver))

    def _set_priority(self):
        import traceback
        import platform #https://stackoverflow.com/questions/110362/how-can-i-find-the-current-os-in-python
        p = psutil.Process(os.getpid()) #source: https://psutil.readthedocs.io/en/release-2.2.1/
        # psutil.ABOVE_NORMAL_PRIORITY_CLASS
        # psutil.BELOW_NORMAL_PRIORITY_CLASS
        # psutil.HIGH_PRIORITY_CLASS
        # psutil.IDLE_PRIORITY_CLASS
        # psutil.NORMAL_PRIORITY_CLASS
        # psutil.REALTIME_PRIORITY_CLASS
        try:
            if platform.system() == 'Windows':
                p.nice(psutil.REALTIME_PRIORITY_CLASS)
            elif platform.system() == 'Linux': #linux FIXIT
                p.nice(-20) # nice runs from -20 to +12, where -20 the most not nice code(highest priority)
        except:
            error(trace.format_exc())
        self.proccess = p

    def init(self, msg_in = None, client = None, driver = None):

        """
        initialize the DL program
        """
        self._init()
        self.start()
        flag = True
        buff = nan
        err = None
        return flag, buff, err

    def help(self):
        """
        return helps string

        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        >>> device.help()
        """
        response = ''
        response += 'This is DI-4108 Data Acquisition Unit python server. \n'
        response += 'Description of the Python Code' + __doc__
        return response

    def close(self):
        """
        orderly close the device program. just a wrapper for self.stop()

        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        >>> device.abort()
        """
        self.stop()

    def abort(self):
        """
        aborts. Currently not implemented

        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        >>> device.abort()
        """
        pass



    def snapshot(self):
        """
        returns a hardcoded snapshot from the device instance. Currently does nothing.

        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        >>> device.snapshot()
        """
        # from numpy import nan
        # err = ''
        # flag = True
        # message = ''
        # response = {}
        # response[b'flag'] = flag
        # response[b'message'] = message
        # response[b'error'] = err
        pass

    def start(self):
        """
        Create a new thread and submits self.run for execution

        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        >>> device.start()
        """
        from ubcs_auxiliary.threading import new_thread
        self.threads['running'] = new_thread(self.run)

    def stop(self):
        """
        Orderly stop of the device code.
        - stops data acquisiion
        - erases all data from USB buffers
        - set digital IO to all high
        - closes usb port connection

        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        >>> device.stop()
        """
        self.running = False
        self.driver.stop_scan()
        self.driver.flush()
        self.set_DIO('1111111') # turns all valves off
        self.driver.close_port()


    def kill(self):
        """
        Orderly self-destruction. kills all threads and deletes the instance.

        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        >>> device.kill()
        """
        self.stop()
        del self

    def config_DL(self,baserate = None,dec = None, DOI_config = None, DOI_set = None):
        """
        configure analog and digital channels, and rate via baserate and dec.

        Parameters
        ----------
        value :: string

        Returns
        -------

        Examples
        --------
        >>> device.config_DL(baserate = 20000, dec = 5, DOI_config = '1111111',DOI_set = '1111111')
        """
        debug('DL: config DL start')
        self.driver.config_channels(baserate = baserate,
                                 dec = dec,
                                 conf_digital = int(DOI_config,2),
                                 set_digital = int(DOI_set,2))
        debug('DL: config DL end')

    def config_DIO(self, value = '00000000'):
        """
        configure direction of digital IOs. It takes a string with 8 characters, '0' or '1' where
        '0' -
        '1' -

        Parameters
        ----------
        value :: string

        Returns
        -------

        Examples
        --------
        >>> device.config_DIO('00000000')
        """
        if self.running:
            driver.config_digital(int(string,2))
            reply = None
        else:
            reply = driver.config_digital(int(string,2), echo = True)
        return reply

    def set_DIO(self, value = '00000000'):
        """
        set digital input/output state

        Parameters
        ----------
        value :: string

        Returns
        -------

        Examples
        --------
        >>> device.DIO = 127
        """
        if isinstance(value,str):
            value = int(value,2)
        self.driver.set_digital(value)
        self.io_push({'dio':value})
        print('set DIO inside device daq library')

    def set_outside_DIO(self, value = '00000000'):
        """
        sets digital input/output state

        Parameters
        ----------
        value :: string

        Returns
        -------

        Examples
        --------
        >>> device.DIO = 127
        """
        if isinstance(value,str):
            value = int(value,2)
        self.driver.set_digital(value)
        print('set DIO inside device daq library')


    def get_DIO(self):
        """
        get digital state from data queue
        """
        return int(self.queue.peek_last_N(3)[-1,9])
    DIO = property(get_DIO,set_DIO)


    ### Advance function


    def run(self):
        """
        This is a main fuction that will execute run_once function on the while running loop. Usually it gets submitted to a separate thread.

        This function collects data and puts it in the Ring Buffer.
        It is run in a separate thread(See main priogram)

        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        >>> device.run()
        """
        from time import strftime, localtime, time
        info('Measurement thread has started')
        self.driver.readall()
        self.running = True
        self.driver.start_scan()
        while self.running:
            self.run_once()
        info('data acquisition thread has stopped')

    def run_once(self):
        """
        the repeated block executed in while running loop in the main run() thread

        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        >>> device.run_once()
        """
        from numpy import array
        data, flag = (self.driver.get_readings(points_to_read = self.pr_packet_size))
        self.data = data
        debug(f'data from one reading cycle of the driver {data.shape}')
        debug(f'the length of pressure sensor is  offset{len(self.pressure_sensor_offset)}')
        pressure_sensor_offset = array(self.pressure_sensor_offset)
        if flag:
            for i in range(8):
                try:
                   data[:,i] = data[:,i] - pressure_sensor_offset[i]
                except:
                    error(traceback.format_exc())
            self.queue.enqueue(data)

        else:
            info('buffer overflow')
            self.running = False

    #####Auxiliary functions
    def parse_binary(self,value = 0):
        """
        takes an integer and converts it to 8 bit representation as an array.
        If float number is passed, it will be converted to int.
        """
        from numpy import arange,ndarray,nan
        value = int(value)
        binary = format(value, '#010b')
        arr = arange(7)
        for i in range(7):
            arr[i] = binary[9-i]
        return arr

    def unparse_binary(self,arr = array([1, 1, 1, 1, 1, 1, 1])):
        """
        takes an integer and converts it to 8 bit representation as an array.
        If float number is passed, it will be converted to int.
        """
        from numpy import arange,ndarray,nan
        integer = 0
        for i in range(len(arr)):
            integer += arr[i]*2**(i)
        return integer

    def set_pressure_sensor_offset(self,dt = 3):
        """
        set pressure sensor offset
        """
        # wait for dt seconds
        # calculated offset and standard deviation
        # assisgn first 8 mean values(analog values) to
        # self.pressure_sensor_offset
        from time import sleep
        sleep(dt)
        freq = int(self.pr_rate)
        offsets = self.queue.peek_last_N(dt*freq).mean(axis = 0)
        stds = self.queue.peek_last_N(dt*freq).std(axis = 0)
        info('Pressure sensors offsets are %r and errors are %r ' %(offsets,stds))
        self.pressure_sensor_offset = offsets[:8]


    ### Input-Output controller section
    def io_push(self,io_dict = None):
        """
        a wrapper that takes care of write command to the io module

        Parameters
        ----------
        io_dict :: dictionary
            a string name of the variable

        Returns
        -------

        Examples
        --------
        >>> self.io_push()
        """
        if self.io_push_queue is not None:
            self.io_push_queue.put(io_dict)

    def io_pull(self, io_dict):
        """
        a wrapper that takes care of 'read' command in the io module

        Parameters
        ----------
        io_dict :: dictionary
            a key-value pairs
        Returns
        -------

        Examples
        --------
        >>> self.io_pull(io_dict = {'key':'value'})
        """
        if self.io_pull_queue is not None:
            for key, value in io_dict.items:
                print(f'received update to {key} to change to {value}')

if __name__ == "__main__": #for testing
    from tempfile import gettempdir
    import logging
    logging.basicConfig(filename=gettempdir()+'/icarus_device.log',
                        level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
    from icarus_nmr.device_daq import Device
    device = Device()
    from icarus_nmr.driver_mock import Driver
    driver = Driver()
    device.bind_driver(driver)
    device.init()
    self = device
