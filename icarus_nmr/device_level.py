"""
DATAQ 4108 Device Level code
author: Valentyn Stadnytskyi
Date: November 2017- April 2019

fully python3 compatible.

The main purpose of this module is to provide useful interface between DI-4108 and a server system level code that does all numbercrynching. This modules only job is to attend DI-4108 and insure that all data is collected and stored in a circular buffer.

The communication in this module is done via XLI module developed by Valentyn Stadnytskyi. This module is based on python sockets.

"""
__version__ = '0.0.0'


import traceback
import psutil, os
import platform #https://stackoverflow.com/questions/110362/how-can-i-find-the-current-os-in-python
p = psutil.Process(os.getpid()) #source: https://psutil.readthedocs.io/en/release-2.2.1/
# psutil.ABOVE_NORMAL_PRIORITY_CLASS
# psutil.BELOW_NORMAL_PRIORITY_CLASS
# psutil.HIGH_PRIORITY_CLASS
# psutil.IDLE_PRIORITY_CLASS
# psutil.NORMAL_PRIORITY_CLASS
# psutil.REALTIME_PRIORITY_CLASS
if platform.system() == 'Windows':
    p.nice(psutil.REALTIME_PRIORITY_CLASS)
elif platform.system() == 'Linux': #linux FIXIT
    p.nice(-20) # nice runs from -20 to +12, where -20 the most not nice code(highest priority)

from numpy import nan, mean, std, nanstd, asfarray, asarray, hstack, array, concatenate, delete, round, vstack, hstack, zeros, transpose, split, unique, nonzero, take, savetxt, min, max
from time import time, sleep
import sys
sys.path.append('/Users/femto-13/All-Projects-on-femto/LaserLab/Software/')

import os.path
import struct
from pdb import pm
from time import gmtime, strftime, time
from logging import debug,info,warn,error
if sys.version_info[0] ==3:
    from persistent_property.persistent_property3 import persistent_property
    keyboard_input = input
    from time import process_time as clock
else:
    from persistent_property.persistent_property import persistent_property
    keyboard_input = raw_input
    from time import clock
from ubcs_auxiliary.threading import new_thread

from struct import pack, unpack
from timeit import Timer, timeit
from XLI.circular_buffer_LL import Queue
from threading import Thread, Event, Timer, Condition
from datetime import datetime
from XLI.precision_sleep import precision_sleep #home-made module for accurate sleep

from XLI.hierarchy_instrumentation import XLevelTemplate, IndicatorsTemplate, ControlsTemplate
class Indicators(IndicatorsTemplate):

    ###Data Acquisision module indicators

    def get(self, value = None):
        response = {}
        response[b'running'] = self.running
        response[b'in_waiting'] = self.in_waiting
        response[b's_packet_size'] = self.s_packet_size
        response[b's_serial_number'] = self.s_serial_number
        response[b's_frequency'] = self.s_frequency
        response[b's_port'] = self.s_port
        response[b's_ip_address'] = self.s_ip_address
        response[b's_firmware'] = self.s_firmware
        response[b'target_pressure'] = self.target_pressure
        response[b'sample_pressure'] = self.sample_pressure
        response[b'last_call_lst'] = self.last_call_lst
        response[b'pressure_sensor_offset'] = self.pressure_sensor_offset

        ###indicators to add

        return response

    def get_running(self):
        """
        returns attribute running

        Parameters
        ----------

        Returns
        -------
        reply: boolean
            flag describing if device level is running or not.

        Examples
        --------
        >>> device.running
        True
        """
        try:
            response = getattr(icarus_dl,'running')
        except:
            response = None #device.controls.running
            warning(traceback.format_exc())
        return response
    def set_running(self,value):
        setattr(icarus_dl,'running',value)
    running = property(get_running,set_running)

    def get_current_values(self):
        from numpy import zeros
        response = {}
        try:
            for key in list(device.buffers.keys()):
                response[key] = device.buffers[key].get_last_N(1)
        except:
            warning(traceback.format_exc())
            response = None
        return response
    current_values = property(get_current_values)

    def get_in_waiting(self):
        """
        returns number of data points waiting in the queue to be read

        Parameters
        ----------

        Returns
        -------
        N: integer
            number of points waiting to be read.

        Examples
        --------
        >>> device.in_waiting
        4000
        """
        try:
            response = icarus_dl.queue.len
        except:
            error(traceback.format_exc())
            response = None
        return response
    in_waiting = property(get_in_waiting)


    def get_test_packet(self, N = 4000):
        """
        returns the test packet of sizeN

        Parameters
        ----------
        N: integer
            size of the test packet.

        Returns
        -------
        data: numpy array
            numpy array

        Examples
        --------
        >>> arr = device.test_packet
        >>> arr.shape()
        (10,4000)
        """
        from numpy import zeros, random, asarray
        array = asarray(random.rand(10,N)*1024, dtype = 'int16')
        return array
    test_packet = property(get_test_packet)


    def get_s_serial_number(self):
        """
        returns serial number of the connected DI-4108 device

        Parameters
        ----------

        Returns
        -------
        serial number: string
            string representaion of the serial number


        Examples
        --------
        >>> sn = device.s_serial_number
        >>> sn
        """
        try:
            return icarus_dl.device_info[b'Serial Number']
        except:
            return None
    s_serial_number = property(get_s_serial_number)

    def get_s_port(self):
        """
        returns server port

        Parameters
        ----------

        Returns
        -------
        server port: integer
            integer number representing the port number open on the server side.


        Examples
        --------
        >>> port = device.s_port
        >>> property
        2030
        """
        return server.port
    s_port = property(get_s_port)

    def get_s_ip_address(self):
        return server.ip_address
    s_ip_address = property(get_s_ip_address)

    def get_s_firmware(self):
        return icarus_dl.device_info[b'Firmware version']
    s_firmware = property(get_s_firmware)

    def get_s_frequency(self):
        return icarus_dl.pr_rate
    s_frequency = property(get_s_frequency)

    def get_s_packet_size(self):
        return icarus_dl.pr_packet_size
    s_packet_size = property(get_s_packet_size)

    def get_target_pressure(self):
        from numpy import mean
        return mean(icarus_dl.queue.buffer[0,icarus_dl.queue.front-100:icarus_dl.queue.front])
    target_pressure = property(get_target_pressure)

    def get_sample_pressure(self):
        from numpy import mean
        return mean(icarus_dl.queue.buffer[5,icarus_dl.queue.front-100:icarus_dl.queue.front])
    sample_pressure = property(get_sample_pressure)

    def get_pressure_sensor_offset(self):
        return icarus_dl.pressure_sensor_offset
    pressure_sensor_offset = property(get_pressure_sensor_offset)



    def get_last_call_lst(self):
        return server.last_call_lst
    last_call_lst = property(get_last_call_lst)









class Controls(ControlsTemplate):

    def get(self):
        response = {}
        response[b'DIO'] = self.DIO
        response[b'DIO_default'] = self.DIO_default


        response[b'pg_period'] = self.pg_period
        response[b'pg_pre_pulse_width'] = self.pg_pre_pulse_width
        response[b'pg_depre_pulse_width'] = self.pg_depre_pulse_width
        response[b'pg_delay_width'] = self.pg_delay_width

        response[b'safe_state'] = self.safe_state
        response[b'trigger_mode'] = self.trigger_mode
        return response

    def set(self,new_controls = {b'temp':False}):
        for key in list(new_controls.keys()):
            setattr(self,key.decode("utf-8"),new_controls[key])
        response = self.get()
        return response


    def set_DIO(self, value = '00000000'):
        if isinstance(value,str):
            value = int(value,2)
        driver.set_digital(value)
        sleep((icarus_dl.pr_packet_size/4000)*1.1)
    def get_DIO(self):
        from time import sleep
        return int(icarus_dl.queue.buffer[9,icarus_dl.queue.front])
    DIO = property(get_DIO,set_DIO)

    def set_DIO_default_pulsed(self,value):
        if isinstance(value,str):
            value = int(value,2)
        icarus_dl.DIO_default = value
    def get_DIO_default_pulsed(self):
        from time import sleep
        return icarus_dl.DIO_default
    DIO_default_pulsed = property(get_DIO_default_pulsed,set_DIO_default_pulsed)
    DIO_default = DIO_default_pulsed

    def set_pg_pre_pulse_width(self, value = 0.007):
        icarus_dl.pg_pre_pulse_width = value
    def get_pg_pre_pulse_width(self):
        return icarus_dl.pg_pre_pulse_width
    pg_pre_pulse_width = property(get_pg_pre_pulse_width,set_pg_pre_pulse_width)

    def set_pg_depre_pulse_width(self, value = 0.007):
        icarus_dl.pg_depre_pulse_width = value
    def get_pg_depre_pulse_width(self):
        return icarus_dl.pg_depre_pulse_width
    pg_depre_pulse_width = property(get_pg_depre_pulse_width,set_pg_depre_pulse_width)

    def set_pg_delay_width(self, value = 0.1):
        icarus_dl.pg_delay_width = value
    def get_pg_delay_width(self):
        return icarus_dl.pg_delay_width
    pg_delay_width = property(get_pg_delay_width,set_pg_delay_width)

    def set_pg_period(self, value = 3):
        icarus_dl.pg_period = value
    def get_pg_period(self):
        return icarus_dl.pg_period
    pg_period = property(get_pg_period,set_pg_period)

    def set_trigger_mode(self, value = 0):
        icarus_dl.trigger_mode = value
    def get_trigger_mode(self):
        return icarus_dl.trigger_mode
    trigger_mode = property(get_trigger_mode,set_trigger_mode)


    def set_safe_state(self, value = 0):
        self.trigger_mode = 0
        from XLI.auxiliary import binary_to_array,array_to_binary
        arr = binary_to_array(self.DIO)
        if arr[0] == 1 and arr[1] == 0 and arr[2] == 0 and self.trigger_mode == 0:
            flag =  1
        else:
            flag =  0
        if value == 1 and flag == 0:
            arr[0] = 1
            self.DIO = array_to_binary(arr)
            sleep(0.3)
            arr[1] = 0
            self.DIO = array_to_binary(arr)
            sleep(0.3)
            arr[2] = 0
            self.DIO = array_to_binary(arr)
    def get_safe_state(self):
        from XLI.auxiliary import binary_to_array
        arr = binary_to_array(self.DIO)
        if arr[0] == 1 and arr[1] == 0 and arr[2] == 0 and self.trigger_mode == 0:
            return 1
        else:
            return 0
    safe_state = property(get_safe_state,set_safe_state)

    def set_bit(self,bit ,value):
        pass


class DI4108_DL(XLevelTemplate):
    pr_serial_number = persistent_property('Serial Number', '00000')
    pr_AI_channels = persistent_property('Number of AI',8)
    pr_DI_channels = persistent_property('Number of DI',1)
    pr_buffer_size = persistent_property('circular buffer size',(10,2400000))
    pr_rate = persistent_property('rate(Hz)', 4000)
    pr_baserate = persistent_property('baserate(Hz)', 20000)
    pr_dec = persistent_property('dec', 5)
    pr_DOI_config = persistent_property('DIO config', '1111111')
    pr_DOI_set = persistent_property('DIO set', '1111111')
    pr_packet_size = persistent_property('packet size', 64)
    pr_packet_buffer_size = persistent_property('pr_paket_buffer_size', 1000)
    pr_os_buffer = persistent_property('os_buffer', 12800)
    pressure_sensor_offset = persistent_property('pressure_sensor_offset',
                                               [69.5595, 65.562, 68.881375, 84.2195, 86.96075, 17.248, 17.322, 0]) # value read at atmoshperic pressure
    pg_period = persistent_property('pg_period', 5.0)
    pg_pre_pulse_width = persistent_property('pg_pre_pulse_width', 0.1)
    pg_depre_pulse_width = persistent_property('pg_depre_pulse_width', 0.1)
    pg_delay_width = persistent_property('pg_delay_width', 0.5)
    trigger_mode = 0
    DIO_default = 126


    inds = Indicators()
    ctrls = Controls()
    def __init__(self):
        self.name = 'DI4108_DL'
        self.device_info = {}
        self.device_info['empty'] = 'empty'
        self.task_name_dict = {}
        self.task_name_dict['empty'] = 'empty'
        self.running = False #this is an old flag for running. Will be depreciated at some point
        self.running = False
        self.packet_pointer = -1
        #Init circular buffer
        self.pr_packet_size = 64
        self.pr_baserate = 20000
        self.pr_dec = 5
        self.pr_rate = (self.pr_baserate)/self.pr_dec
        self.pr_buffer_size = (10,int(self.pr_packet_size*self.pr_rate))
        self.queue = Queue(size = self.pr_buffer_size, var_type = 'int16')
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


    def init_driver(self):
        self.driver.init()

    def init(self, msg_in = None, client = None):

        """
        initialize the DL program
        """
        #from DI4108_BULK_driver import driver
        self.driver = driver
        self.driver.init()
        self.device_info = {**self.driver.get_hardware_information(),**self.device_info}
        self.stop()
        self.config_DL()
        self.start()
        flag = True
        buff = nan
        err = None
        return flag, buff, err

    def help(self, msg_in = None, client = None):
        response = ''
        response += 'This is DI-4108 Data Acquisition Unit python server. \n'
        response += 'Description of the Python Code' + __doc__
        return response

    def close(self):
        """
        close the DL program
        """
        self.stop()
        flag = True
        buff = nan
        err = None
        return flag, buff, err

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

    def snapshot(self):
        from numpy import nan
        err = ''
        flag = True
        message = ''


        response = {}
        response[b'flag'] = flag
        response[b'message'] = message
        response[b'error'] = err
        return response

    def execute_action(self, time = '', action = ''):
        flag = False
        result_dic = {}
        err = ''
        return flag,result_dic,err

    def start(self):
        if sys.version_info[0] ==3:
            from ubcs_auxiliary.threading import new_thread
        else:
            from thread import start_new_thread as new_thread
        new_thread(self.run,())

    def stop(self):
        self.running = False
        self.driver.stop_scan()
        self.driver.flush()
        self.set_DIO('1111111') # turns all valves off
        self.driver.close_port()


    def GUI_safe_stop(self):
        self.running = False
        self.driver.stop_scan()
        self.driver.flush()

        self.set_DIO('1111111') # turns all valves off
        self.driver.close_port()
        del self


    def getRingBufferN(self,N,pointer):
        #print('input: N= %r ; pointer = %r )' % (N, pointer))
        if pointer > (self.pPacketBufferSize+1)*self.pr_packet_size:
            pointer = pointer - ((self.pPacketBufferSize+1)*self.pr_packet_size)-1
        try:
            #print(' try: N= %r ; pointer = %r' % (N, pointer))
            res = self.ring_buffer.get_N(N, pointer)
        except:
            res = nan
        return res

    def get_packet_ij(self,i,j): #return from i to j
        if j >= i:
            #print(i,j)
            result = self.ring_buffer.get_N((j-i+1)*self.pr_packet_size,(j+1)*self.pr_packet_size-1)
        else:
            result = nan
        return result

    def config_DL(self):
        debug('DL: config DL start')
        self.driver.config_channels(baserate = self.pr_baserate,
                                 dec = self.pr_dec,
                                 conf_digital = int(self.pr_DOI_config,2),
                                 set_digital = int(self.pr_DOI_set,2))
        debug('DL: config DL end')



    def config_DIO(self, string = '00000000'):
        if self.running:
            driver.config_digital(int(string,2))
        else:
            driver.config_digital(int(string,2), echo = True)

    def set_DIO(self, value = '00000000'):
        #from DI4108_BULK_driver import driver
        if isinstance(value,str):
            value = int(value,2)
        self.driver.set_digital(value)
    def get_DIO(self):
        return int(self.queue.buffer[9,self.queue.front])
    ### Advance function


    def run(self):
        from time import strftime, localtime, time
        """
        This function collects data and puts it in the Ring Buffer.
        It is run in a separate thread(See main priogram)
        """
        info('Measurement thread has started')
        #sleep(10)
        self.driver.readall()
        #tested dec 20, 2017
        time_start = time()
        #there is command device.ser.is_open which supposed to return True or False.
        #I tried it just before I left on Dec 21, but it was giving me errors.
        #The device._waiting()[0]  is causing the big read error when the Stop_SL function is run.
        #the 3 lines added below and commented out should fix it. But the code needs to be tested again.
        #plt.figure(1)
        self.running = True
        counter = 0
        self.Gcounter = 0
        self.time_crash = clock()
        self.driver.start_scan()
        self.arr = zeros((10,10))
        i=0
        time_gstart = clock()
        self.event = False
        self.OverflowFlag = False
        while self.running:
            data, flag = (self.driver.get_readings(points_to_read = self.pr_packet_size))
            self.data = data
            if flag and self.running:
                for i in range(8):
                    try:
                       data[i,:] = data[i,:] - self.pressure_sensor_offset[i]
                    except:
                        error(traceback.format_exc())
                self.queue.enqueue(data)

            else:
                info('buffer overflow')
                self.running = False

        warn('thread is done')

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

    #####TASKS
    def pulse(self, valve = 1, duration = 0.007, precision = True, echo = False):
        """
        generates a pulse at a given valve.
        Parameters:
        valve: integer 1 - Depressure; 2 - Pressure;  4 - High Pressure pump; -1 - wait
        duration: in seconds
        precision: 1 - presicion sleep; 2 - normal sleep;
        echo: True or False - this is an absolute parameter
        """
        from time import clock, time, sleep,perf_counter
        t1 = perf_counter()
        def toggle(bit = 0):
            if bit == 0:
                bit = 1
            elif bit == 1:
                bit = 0
            else:
                bit = None
            return bit
        from precision_sleep import precision_sleep
        psleep = precision_sleep.psleep
        if valve == -1:
            valve_bit = int('0000000',2) # Wait

        #get current state
        curr_DIO = self.get_DIO()
        arr_DIO = self.parse_binary(curr_DIO)
        arr_DIO[valve] = toggle(arr_DIO[valve])
        if valve >= 0 and self.trigger_mode == 1:
            self.set_DIO(self.unparse_binary(arr_DIO))
        t2 = perf_counter()
        if precision:
            precision_sleep.psleep(duration-(t2-t1))
        else:
            sleep(duration)
        arr_DIO[valve] = toggle(arr_DIO[valve])
        if valve >= 0 and self.trigger_mode == 1:
            self.set_DIO(self.unparse_binary(arr_DIO)) # up

    def pulse_sequence(self):
        icarus_dl.ctrls.DIO = 127-4;
        sleep(0.1);
        icarus_dl.ctrls.DIO = 127;
        sleep(0.5);
        icarus_dl.ctrls.DIO = 127-2;
        sleep(0.007);
        icarus_dl.ctrls.DIO = 127;

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
        from time import sleep
        from numpy import mean, std
        sleep(N)
        offsets = mean(icarus_dl.queue.buffer[:,icarus_dl.queue.front-4000*N:icarus_dl.queue.front],\
                       axis = 1)
        stds = std(icarus_dl.queue.buffer[:,icarus_dl.queue.front-4000*N:icarus_dl.queue.front],\
                       axis = 1)
        print('Pressure sensors offsets are %r and errors are %r ' %(offsets,stds))
        self.pressure_sensor_offset = offsets[:8]

class Pulse_Generator():

    bit_HPpump = 0b1
    bit_valve1 = 0b10
    bit_valve2 = 0b100
    bit_valve3 = 0b1000
    bit_log = 0b10000
    flag_play_sequence = False
    sequence_string = 'i4L,i1L,w_150_ms,i1H,w_300_ms,i2L,w_30_ms,i2H,w_100_ms,i3L,w_500_ms,i3H,w_2_s'
    pr_pulse_generator_counter = 0


    def __init__(self):
        self.name = 'PulseGenerator'
        self.curr_DIO = icarus_dl.ctrls.DIO_default
        self.running = False
        self.console_running = False

    def init(self):
        from numpy import nan
        self.trigger_mode = 0  # can be int (1) or ext (0) Always start with console
        #self.set_trigger_mode(value = self.trigger_mode)

        self.running = False

        self.curr_DIO = int('1111111',2)


    def set_DIO(self, command):
        """
        a wrapper for communicate with DI-4108
        -input-
        command: an integer 0 to 127 defining the state of digital input\output
        -return-
        nothing
        """
        try:
            icarus_dl.ctrls.set_DIO(command)
        except:
            error(traceback.format_exc())

    def get_DIO(self):
        """
        a wrapper for communicate with DI-4108
        -input-
        command: an integer 0 to 127 defining the state of digital input\output
        -return-
        nothing
        """
        try:
            value = icarus_dl.ctrls.get_DIO()
        except:
            error(traceback.format_exc())
            value = nan
        return value


    def pulse(self, valve = 1, duration = 1, precision = True, echo = False):
        """
        generates a pulse at a given valve.
        Parameters:
        valve: integer 1 - Depressure; 2 - Pressure;  4 - High Pressure pump; -1 - wait
        duration: in seconds
        precision: 1 - presicion sleep; 2 - normal sleep;
        echo: True or False - this is an absolute parameter
        """
        if valve == 1:
            valve_bit = int(self.bit_valve1) # Depressure
        elif valve == 2:
            valve_bit = int(self.bit_valve2) # Pressure
        elif valve == 3:
            valve_bit = int(self.bit_valve3) # Pressure
        elif valve == 4:
            valve_bit = int(self.bit_HPpump) # High pressure valve
        elif valve == -1:
            valve_bit = int('0000000',2) # Wait
        else:
            valve_bit = int('0000000',2) # Wait if valve selection is not recognized
        curr_DIO = icarus_dl.ctrls.DIO_default
        new_DIO = curr_DIO-valve_bit
        if valve_bit != 0 and self.trigger_mode != 0:
            driver.set_digital(new_DIO) #down
        if precision:
            precision_sleep.psleep(duration)
        else:
            sleep(duration)
        if valve_bit != 0 and self.trigger_mode != 0:
            driver.set_digital(curr_DIO) # up
        debug('DIO %r -> %r -> %r' % (curr_DIO,new_DIO,curr_DIO))



    def pulse_sequence(self,pvname = '',value = '', char_val = ''):
        """
        the pulse sequence:
            Depressure for tw1 miliseconds
            Wait for td miliseconds
            Pressure for tw2 miliseconds
        input: None; Output: None

        Because we acquire data at 1kHz with packet size of 128, which make is
        128 ms, we have to get current state at the very beggining of the
        sequence
        """
        self.pulse(valve = 1, duration = self.tw1)
        self.pulse(valve = -1, duration = (self.td-self.tw1)) #-1 stands for waiting
        self.pulse(valve = 2, duration = self.tw2)
        self.pr_pulse_generator_counter += 1

    def set_pump_state(self,value = None):
        """
        pump is open if value = 0 and closed if value = 1
        """
        from XLI.server_LL import server
        self.curr_DIO = int(self.get_DIO())
        try:
            if value*(self.bit_HPpump) != self.curr_DIO & self.bit_HPpump:
                if value == 1:
                    self.set_DIO(self.curr_DIO + self.bit_HPpump)
                    self.curr_DIO = self.curr_DIO + self.bit_HPpump
                elif value == 0:
                    self.set_DIO(self.curr_DIO - self.bit_HPpump)
                    self.curr_DIO = self.curr_DIO - self.bit_HPpump
                    self.set_safe_state(value = 0) #Problem is here!
        except:
            error(traceback.format_exc())

    def get_pump_state(self):
        return int((self.get_DIO()& self.bit_HPpump) / self.bit_HPpump)

    def set_pressurize_state(self,value = ''):

        bit = self.bit_valve2
        self.curr_DIO = int(self.get_DIO())
        #print('current_digital',current_digital)
        try:
            if value*(bit) != self.curr_DIO & bit:
                if value == 1:
                    self.set_DIO(self.curr_DIO + bit)
                    self.curr_DIO = self.curr_DIO + bit
                elif value == 0:
                    self.set_DIO(self.curr_DIO - bit)
                    self.curr_DIO = self.curr_DIO - bit
        except:
            error(traceback.format_exc())
        #if len(pvname) == 0:
            #casput(socket_server.CAS_prefix + 'pressurize_state',value)
    def get_pressurize_state(self):
        from XLI.auxiliary import parse_binary,unparse_binary
        arr = parse_binary(self.get_DIO())
        return arr[2]

    def set_depressurize_state(self,value = None):
        from XLI.auxiliary import parse_binary,unparse_binary
        bit = self.bit_valve1
        curr_DIO = int(self.get_DIO())
        arr = parse_binary(curr_DIO)
        #print('current_digital',current_digital)
        if value == 0 or value == 1:
            arr[1] = value
        number = unparse_binary(arr)
        self.set_DIO(number)

    def get_depressurize_state(self):
        from XLI.auxiliary import parse_binary,unparse_binary
        arr = parse_binary(self.get_DIO())
        return arr[1]

    def set_log_bit_state(self,value = None):
        """
        sets the bit 4 to the passed value. Bit 4 is logging bit.
        """
        from XLI.auxiliary import parse_binary,unparse_binary
        curr_DIO = int(self.get_DIO())
        arr = parse_binary(curr_DIO)
        #print('current_digital',current_digital)
        if value == 0 or value == 1:
            arr[4] = value
        number = unparse_binary(arr)
        self.set_DIO(number)
        server.push_subscribed_updates(controls = [b'log_bit_state'])

    def get_log_bit_state(self):
        from XLI.auxiliary import parse_binary,unparse_binary
        arr = parse_binary(self.get_DIO())
        return arr[4]

    def pressurize_pulse(self,pvname = '',value = '', char_val = ''):
        #self.curr_DIO = self.get_DIO()
        self.pulse(valve = 2, duration = self.tw2/1000.)



    def depressurize_pulse(self,pvname = '',value = '', char_val = ''):
        #self.curr_DIO = self.get_DIO()
        self.pulse(valve = 1, duration = self.tw1/1000.)



    def run(self):
        """
        the while True loop with pulse generator.
        it has to run all the time for high pressure pump pulse to
        be generated properly.
        important parameters: trigger: 0 manual, 1 -internal; 2 - external
        """
        from time import clock, time
        from event_detector_LL import event_detector

        self.set_DIO(icarus_dl.ctrls.DIO_default)
        sleep(0.3)
        self.curr_DIO  = self.get_DIO()
        self.running = True
        self.paused = False
        self.meas = {}
        self.meas['period'] = self.period
        manual_flag = True
        self.console_counter = 0
        self.update_period = 0.5
        while self.running:
            #print(pulse_generator.console_counter)
            if self.trigger_mode == 0:
                if not manual_flag:
                    info('pulse Generator thread: set pump default')
                    #self.set_pump_to_default()
                    manual_flag = True
                self.console_counter = 0
                sleep(self.update_period)
                self.shutdown_flag = False
            elif self.trigger_mode == 1:
                if manual_flag:
                    icarus_dl.ctrls.DIO = icarus_dl.ctrls.DIO_default_pulsed
                    manual_flag = False
                #pulse_valve3_duration = 0.02
                #self.pulse(valve = 3, duration = pulse_valve3_duration)#comment this
                self.length_of_pulse_sequence = self.td + self.tw2
                self.pulse_sequence() #uncomment this

                time_to_sleep = self.period -self.length_of_pulse_sequence
                Nsteps = time_to_sleep/self.update_period
                tstart = time()
                time_left = time_to_sleep - time() + tstart
                while time_left>0:
                    if self.trigger_mode == 0:
                        time_left = -1
                        break
                    if time_left> self.update_period:
                        sleep(self.update_period)
                    else:
                        precision_sleep.psleep(time_left)
                    time_left = time_to_sleep - time() + tstart

                self.console_counter = 0
            elif self.trigger_mode == 2:
                if manual_flag:
                    self.set_pump_state(value = 0)
                    manual_flag = False
                else:
                    pass
                self.length_of_pulse_sequence = self.td + self.tw2
                time_to_sleep = self.period
                Nsteps = time_to_sleep/self.update_period
                tstart = time()
                time_left = time_to_sleep - time() + tstart
                while time_left>0:
                    if (self.shutdown_flag or self.trigger_mode == 0):
                        time_left = -1
                        break
                    if time_left> self.update_period and time_left>0:
                        sleep(self.update_period)
                    else:
                        precision_sleep.psleep(time_left)
                    time_left = time_to_sleep - time() + tstart
            elif self.trigger_mode == 3:
                try:
                    lst = self.decode_sequence(self.sequence_string)
                    self.play_sequence(lst = lst)
                except:
                    sleep(self.update_period)
                    error(traceback.format_exc())





        self.running = False
        self.paused = True


    def get_deprepulse_width(self):
        return self.tw1
    def set_deprepulse_width(self,value = ''):
        value = float(value)
        self.tw1 = value
        #if len(pvname) == 0:
            #casput(socket_server.CAS_prefix+'PG_deprepulse_width',value)

    def get_delay_width(self):
        return self.td
    def set_delay_width(self,value = ''):
        value = float(value)
        self.td = value


    def get_prepulse_width(self):
        return self.tw2
    def set_prepulse_width(self,value = ''):

        value = float(value)

        self.tw2 = value
        #if len(pvname) == 0:
            #casput(socket_server.CAS_prefix+'PG_prepulse_width',value)

    def get_period(self):
        return icarus_dl.ctrls.pg_period
    def set_period(self,value = 0):
        icarus_dl.ctrls.pg_period = value
    period = property(get_period,set_period)

    def get_tw1(self):
        return icarus_dl.ctrls.pg_depre_pulse_width
    def set_tw1(self,value = 0):
        icarus_dl.ctrls.pg_depre_pulse_width = value
    tw1 = property(get_tw1,set_tw1)

    def get_tw2(self):
        return icarus_dl.ctrls.pg_pre_pulse_width
    def set_tw2(self,value = 0):
        icarus_dl.ctrls.pg_pre_pulse_width = value
    tw2 = property(get_tw2,set_tw2)

    def get_td(self):
        return icarus_dl.ctrls.pg_delay_width
    def set_td(self,value = 0):
        icarus_dl.ctrls.pg_delay_width = value
    td = property(get_td,set_td)

    def get_safe_state(self):
        return icarus_dl.ctrls.safe_state
    def set_safe_state(self,value = 0):
        icarus_dl.ctrls.safe_state = value
    safe_state = property(get_safe_state,set_safe_state)




    def get_trigger_mode(self):
        """
        returns trigger mode from pulse_generator instance
        """
        return icarus_dl.ctrls.trigger_mode
    def set_trigger_mode(self,value = ''):
        """
        sets trigger mode either from CA monitor or manually via value variable
        """
        value = int(value)
        if value == 0 or value == 1 or value == 2 or value == 3:
            curr_trigger_mode = self.trigger_mode
            icarus_dl.ctrls.trigger_mode = value
    trigger_mode = property(get_trigger_mode,set_trigger_mode)






    def start(self):
        """
        for back competibility with older SL codes does nothing
        """
        from _thread import start_new_thread
        if not self.running:
            start_new_thread(self.run,())

    def stop(self):
        self.set_DIO(self.default_state)
        self.running = False

    def close(self):
        self.stop()

    def decode_sequence(self,string):
        string1 = string
        string1 = string1.replace(',','","')
        string1 = string1.replace('[','["')
        string1 = string1.replace('["["','[["')
        string1 = string1.replace('["["["','[[["')
        string1 = string1.replace(']','"]')
        string1 = string1.replace(']"]',']]')
        string1 = string1.replace(']"]"]',']]]')
        return eval(string1)

    def play_sequence(self,lst):
        """
    bit_HPpump = persistent_property('bit_HPpump',0b1)
    bit_valve1 = persistent_property('bit_valve1',0b10)
    bit_valve2 = persistent_property('bit_valve2',0b100)
    bit_valve3 = persistent_property('bit_valve3',0b1000)
    bit_log = persistent_property('bit_log',0b10000)
    """
        #set_log_bit_state,set_depressurize_state,set_pressurize_state,set_pump_state
        from time import time, sleep
        flag = True
        for item in lst:
            if flag:
                if (item[0] == 'i' or item[0] == 'I'):
                    if (item[2] =='L' or item[2] =='l'):
                        value = 0
                    elif (item[2] == 'H' or item[2] == 'h'):
                        value = 1
                    else:
                        value = 0
                    if item[1] == '1':
                        self.set_depressurize_state(value = value)
                    elif item[1] == '2':
                        self.set_pressurize_state(value = value)
                    elif item[1] == '3':
                        self.set_pump_state(value = value)
                    elif item[1] == '4':
                        self.set_log_bit_state(value = value)
                    elif item[1] == '5':
                        pass#self.set_log_bit_state(pvname = ' ', value = value)
                    else:
                        pass

                elif item[0] == 'w':
                    local_lst = item.split('_')
                    if len(local_lst) == 3:
                        if local_lst[2] == 'ms':
                            gain = 10**-3
                        elif local_lst[2] == 's':
                            gain = 1
                        else:
                            gain = 1
                        try:
                            flt = float(local_lst[1])
                        except:
                            error(traceback.format_exc())
                            flt = 1
                    time_to_sleep = flt*gain
                    #precision_sleep.psleep(time_to_sleep)
                    tstart = time()
                    time_left = time_to_sleep - time() + tstart
                    while time_left>0:
                        if (self.trigger_mode != 3):
                            flag = False
                            time_left = 0.01
                        precision_sleep.psleep(time_left)
                        time_left = time_to_sleep - time() + tstart
                else:
                    pass
        if flag:
            self.set_trigger_mode(value = 0)

import sys
try:
    first_arg = sys.argv[1]
except:
    first_arg = 'simulator'

if first_arg == 'device':
    from XLI.drivers.DI4108.DI4108_BULK_driver import driver
elif first_arg == 'simulator':
    from XLI.drivers.DI4108.DI4108_SIMULATOR_driver import driver



if len(sys.argv) == 1:
    local = True
else:
    local = False


if __name__ == "__main__": #for testing
    from tempfile import gettempdir
    import logging
    logging.basicConfig(filename=gettempdir()+'/di4108_DL.log',
                        level=logging.WARN, format="%(asctime)s %(levelname)s: %(message)s")


    icarus_dl = DI4108_DL()
    if first_arg == 'simulator':
        icarus_dl.name = icarus_dl.name + 'simulator'
    pulse_generator = Pulse_Generator()
    pulse_generator.start()

    from XLI.server_LL import Server_LL
    server = Server_LL()
    server.init_server(name = 'icarus-DL')
    server.commands[b'init'] = icarus_dl.init
    server.commands[b'help'] = icarus_dl.help
    server.commands[b'snapshot'] = icarus_dl.snapshot
    #server.commands[b'close'] = device.close
    server.commands[b'controls'] = icarus_dl.controls
    server.commands[b'indicators'] = icarus_dl.indicators
    #server.commands[b'retrieve_values'] = device.retrieve_values
    server.commands[b'subscribe'] = server.subscribe
    server.commands[b'read_queue'] = icarus_dl.read_queue
    #server.commands[b'dump_buffers'] = icarus_SL.subscribe


    msg = 'DI4108 Data Acquisiion server is running. \n'
    msg += 'The server port %r and ip-address %r' %(server.port,server.ip_address)
    icarus_dl.init()
    print(msg)
    print(icarus_dl.name)
    if local:
        pass
    else:
        keyboard_input("Press enter to exit:")
        server.stop()
