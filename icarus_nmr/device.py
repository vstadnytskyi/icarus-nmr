"""
DATAQ 4108 Device Level code
author: Valentyn Stadnytskyi
Date: November 2017- November 2019

fully python3 compatible.

The main purpose of this module is to provide useful interface between DI-4108 and a server system level code that does all numbercrynching. This modules only job is to attend DI-4108 and insure that all data is collected and stored in a circular buffer.

The communication in this module is done via XLI module developed by Valentyn Stadnytskyi. This module is based on python sockets.

"""
__version__ = '0.0.0'


import traceback
import psutil, os


from numpy import nan, mean, std, nanstd, asfarray, asarray, hstack, array, concatenate, delete, round, vstack, hstack, zeros, transpose, split, unique, nonzero, take, savetxt, min, max
from time import time, sleep
import sys
#sys.path.append('/Users/femto-13/All-Projects-on-femto/LaserLab/Software/')

import os.path
import struct
from pdb import pm
from time import gmtime, strftime, time
from logging import debug,info,warning,error
# see https://vstadnytskyi.github.io/auxiliary/saved-property.html for details


if sys.version_info[0] ==3:
    keyboard_input = input
    from time import process_time as clock
else:
    keyboard_input = raw_input
    from time import clock



from struct import pack, unpack
from timeit import Timer, timeit
from circular_buffer_numpy.queue import Queue
from threading import Thread, Event, Timer, Condition
from datetime import datetime

from ubcs_auxiliary.saved_property import DataBase, SavedProperty
from ubcs_auxiliary.threading import new_thread
from ubcs_auxiliary.advsleep import precision_sleep #home-made module for accurate sleep
from ubcs_auxiliary.XLI.hierarchy_instrumentation import XLevelTemplate, IndicatorsTemplate, ControlsTemplate

class DI4108_DL(XLevelTemplate):
    db = DataBase(root = 'TEMP', name = 'DI4108_DL')
    pr_serial_number = SavedProperty(db,'Serial Number', '00000').init()
    pr_AI_channels = SavedProperty(db,'Number of AI',8).init()
    pr_DI_channels = SavedProperty(db,'Number of DI',1).init()
    pr_buffer_size = SavedProperty(db,'circular buffer size',(10,2400000)).init()
    pr_rate = SavedProperty(db,'rate(Hz)', 4000).init()
    pr_baserate = SavedProperty(db,'baserate(Hz)', 20000).init()
    pr_dec = SavedProperty(db,'dec', 5).init()
    pr_DOI_config = SavedProperty(db,'DIO config', '1111111').init()
    pr_DOI_set = SavedProperty(db,'DIO set', '1111111').init()
    pr_packet_size = SavedProperty(db,'packet size', 64).init()
    pr_packet_buffer_size = SavedProperty(db,'pr_paket_buffer_size', 1000).init()
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

    def first_time_setup(self):
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
        returns helps string

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
        orderly closes the device program. just a wrapper for self.stop()

        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        >>> device.abort()
        """
        self.stop()
        flag = True
        buff = nan
        err = None
        return flag, buff, err

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
        from numpy import nan
        err = ''
        flag = True
        message = ''
        response = {}
        response[b'flag'] = flag
        response[b'message'] = message
        response[b'error'] = err
        return response

    def start(self):
        """
        Creates a new thread and submits self.run for execution

        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        >>> device.start()
        """
        from ubcs_auxiliary.threading import new_thread
        new_thread(self.run)

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
        configures analog and digital channels, and rate via baserate and dec.

        Parameters
        ----------
        value :: string

        Returns
        -------

        Examples
        --------
        >>> device.config_DIO('00000000')
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
        else:
            driver.config_digital(int(string,2), echo = True)

    def set_DIO(self, value = '00000000'):
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
    def get_DIO(self):
        return int(self.queue.buffer[self.queue.rear,9])
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
                   data[i,:] = data[i,:] - pressure_sensor_offset[i]
                except:
                    error(traceback.format_exc())
            self.queue.enqueue(data)

        else:
            info('buffer overflow')
            self.running = False


    def read_queue(self, msg_in = {b'number':0}, client = None):
        """
        returns N points from the queue
        """
        response = {}
        flag = True
        err = ''
        try:
            N = msg_in[b'number']
        except:
            N = 0
            flag = False
            err+= traceback.format_exc()
        data = self.queue.dequeue(N = N)
        response[b'message'] = data
        response[b'flag'] = flag
        response[b'err'] = err
        return response

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

    def set_pressure_sensor_offset(self,N = 3):
        """
        """
        from time import sleep
        from numpy import mean, std
        sleep(N)
        offsets = mean(self.object.queue.buffer[:,self.object.queue.rear-4000*N:self.object.queue.rear],\
                       axis = 1)
        stds = std(self.object.queue.buffer[:,self.object.queue.rear-4000*N:self.object.queue.rear],\
                       axis = 1)
        print('Pressure sensors offsets are %r and errors are %r ' %(offsets,stds))
        self.pressure_sensor_offset = offsets[:8]


    ### Input-Output controller section
    def io_write(self, name = None, value = None):
        """
        a wrapper that takes care of write command to the io module

        Parameters
        ----------
        name :: string
            a string name of the variable
        value :: object
            the new value of the variable to be written to the io

        Returns
        -------

        Examples
        --------
        >>> self.io_write()
        """
        pass

    def io_read(self, name = None, value = None):
        """
        a wrapper that takes care of 'read' command to the io module

        Parameters
        ----------
        name :: string
            a string name of the variable
        value :: object
            the new value of the variable to be read from the io module

        Returns
        -------

        Examples
        --------
        >>> self.io_read()
        """
        pass

    def io_execute(self, name = None, value = None):
        """
        a wrapper that processes incoming calls from the IO

        Parameters
        ----------
        name :: string
            a string name of the variable
        value :: object
            the new value of the variable to be assigned

        Returns
        -------

        Examples
        --------
        >>> self.io_execute()
        """
        pass

    # tests in progress

    # Old function with unknown purpose
    def submit_DIO(self,digital):
        """
        set DIO command
        """
        self.set_DIO(digital)
        flag = True
        buff = nan
        err = None
        return flag, buff, err

    def get_all_buffer(self):
        flag = True
        buff = nan
        err = None
        buff = self.ring_buffer.buffer
        return flag, buff,err

    def grab_buffer(self,pointers = (nan,nan)):
        if pointers[1] == 0:
            pointers[1] = self.ring_buffer.pointer
        array = self.ring_buffer.buffer[0,:]
        flag = False
        err = ''
        try:
            buff = self.ring_buffer.buffer[:,pointers[0]:pointers[1]]
            flag = True
        except Exception:
            err += traceback.format_exc()
            error(traceback.format_exc())
        return flag,buff,err




if __name__ == "__main__": #for testing
    from tempfile import gettempdir
    import logging
    logging.basicConfig(filename=gettempdir()+'/di4108_device.log',
                        level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
    from icarus_nmr.device import DI4108_DL
    device = DI4108_DL()
    from icarus_nmr.mock_driver import Driver
    driver = Driver()
    device.bind_driver(driver)
    device.init()
