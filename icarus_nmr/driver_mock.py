"""
DATAQ 4108 driver level code
author: Valentyn Stadnytskyi
"""

from numpy import nan, mean, std, asarray, array, concatenate, \
     delete, round, vstack, hstack, zeros, transpose, split
from time import time, sleep

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
from time import gmtime, strftime
import logging
from struct import pack, unpack
from timeit import Timer
from logging import info,warn, debug, error
import traceback

mock_commands = {}
mock_commands['info 1 \r'] = 'info 1  4108\r'
mock_commands['info 2 \r'] = 'info 2  VS\r'
mock_commands['info 3 \r'] = 'info 3  4A\r'
mock_commands['info 4 \r'] = 'info 4  1234567890\r'
mock_commands['info 5 \r'] = 'info 5  Mary_Smith\r'
mock_commands['info 6 \r'] = 'info 6  00000000\r'
mock_commands['info 7 \r'] = 'info 7  00000000\r'
mock_commands['info 8 \r'] = 'info 8  1\r'
mock_commands['info 9 \r'] = 'info 9  60000000\r'
mock_commands['led 1 \r'] = 'led 1 \r'
mock_commands['led 2 \r'] = 'led 2 \r'
mock_commands['led 3 \r'] = 'led 3 \r'
mock_commands['led 4 \r'] = 'led 4 \r'
mock_commands['led 5 \r'] = 'led 5 \r'


class Driver(object):
    def __init__(self):
        self.available_ports = []
        self.dev = None
        self.sim_analog = [11000,0,8000,0,8000,11000,9000,0]
        self.sim_analog_std = [30,30,30,30,30,30,30,30]
        self.sim_digital = 127
        self.sim_last_read = time()
        self.sim_pressure_state = 1
        self.pump_freq = 1#0.99995
        self.sim_slow_leak_start_time = time()
        self.sim_slow_leak_tau = 60000

        self.sim_flag = False

        from icarus_nmr.tests.test_data.mock_driver import traces

        self.lst_pre = traces.get_lst_pre_trace()
        self.lst_depre = traces.get_lst_pre_trace()
        self.lst_pump = traces.get_lst_pump_trace()

    def init(self):
        self.discover()
        self.use_port()
        self.sim_pump_event_flag = False
        self.sim_pre_event_flag = False
        self.sim_depre_event_flag = False

        info("initialization of the driver is complete")

    def get_information(self):
        """
        emulates retrieval of information via usb. Creates two new atrbiutes to the class: self.dev_dict and self.epi_dict

        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        >>> mock.get_information()
        """
        if self.dev != None:
            self.dev_dict = {}
            self.epi_dict = {}
            self.dev_dict['DEV:address'] = 'DEV:address:simulator'
            self.dev_dict['DEV:bDeviceClass'] = 'DEV:bDeviceClass:simulator'
            self.dev_dict['DEV:bDescriptorType'] = 'DEV:bDescriptorType:simulator'
            self.dev_dict['DEV:bDeviceProtocol'] = 'DEV:bDeviceProtocol:simulator'
            self.dev_dict['DEV:bLength'] = 'DEV:bLength:simulator'
            self.dev_dict['DEV:bMaxPacketSize0'] = 'DEV:bMaxPacketSize0:simulator'
            self.dev_dict['DEV:bNumConfigurations'] = 0
            self.dev_dict['DEV:manufacturer'] = 0
            self.dev_dict['DEV:serial_number'] = 0
            self.dev_dict['DEV:speed'] = 0
            self.dev_dict['DEV:product'] = 0

            #endpoint IN description
            self.epi_dict['EPI:bmAttributes'] = 0
            self.epi_dict['EPI:wMaxPacketSize'] = 0
            self.epi_dict['EPI:bSynchAddress'] = 0
            self.epi_dict['EPI:bInterval'] = 0
            self.epi_dict['EPI:bEndpointAddress'] = 0
            self.epi_dict['EPI:bDescriptorType'] = 0
            self.epi_dict['EPI:bInterval'] = 0
            self.epi_dict['EPI:bInterval'] = 0

    def get_hardware_information(self):
        """
        emulates retrieval of information via usb. Creates two new atrbiutes to the class: self.dev_dict and self.epi_dict

        Parameters
        ----------

        Returns
        -------
        dic :: dictionary
            dictionary of hardware information

        Examples
        --------
        >>> dic = mock.get_hardware_information()
        >>> dic

        """

        dic = {}
        dic[b'Device name'] = self.inquire('info 1 \r').split('info 1 ')[1][1:-1]
        dic[b'Firmware version'] = self.inquire('info 2 \r').split('info 2 ')[1][1:-1]
        dic[b'Serial Number'] = self.inquire('info 6 \r').split('info 6 ')[1][1:-1]
        dic[b'Sample Rate Divisor'] = self.inquire('info 9 \r').split('info 9 ')[1][1:-1]

        return dic



    def use_port(self, port = ''):
        pass

    def discover(self):
        self.dev = 0


    """Set and Get persistent_property"""
    # functions for persistent properties if needed

    """Basic serial communication functions"""

    def read(self,N):

        while time() - self.sim_last_read <= N/4000.0:#512.0/4000.0:
            sleep(0.01)
        self.sim_last_read = time()
        return True

    def readall(self):
        """
        reads all information in the usb buffer

        Parameters
        ----------

        Returns
        -------
        buffer :: string
            buffer information as a string

        Examples
        --------
        >>> dic = mock.get_hardware_information()
        >>> dic
        """
        return self.read(0)

    def write(self,command):
        """
        writes into USB buffer

        Parameters
        ----------
        command :: string
            a string representation of a command

        Returns
        -------

        Examples
        --------
        >>> mock.write(command = 'info 1 \\r')
        """
        try:
            self.dev.write(self.epo,command)
        except:
            error(traceback.format_exc())

    def inquire(self,command):
        if command in list(mock_commands.keys()):
            res = mock_commands[command]
        else:
            res = 'Command not found\r\x00'
        return res

    def flush(self):
        pass

    def close_port(self):
        pass
    """DI-4108 Communcation functions"""

    def config_digital(self, number = 127, echo = False):
        #tested dec 17, 2017
        return True

    def parse_binary_number(self,value = 0, Nbits = 7):
        """
        parses integer number into bits and represents them as an array

        Parameters
        ----------
        value :: integer
            integer number

        Returns
        -------

        Examples
        --------
        >>> mock.write(command = 'info 1 \\r')
        """
        from numpy import arange,ndarray,nan
        binary = format(value, '#0'+str(Nbits+3)+'b')
        arr = arange(Nbits)
        for i in range(Nbits):
            arr[i] = binary[Nbits+2-i]
        return arr

    def set_digital(self, number = 127, echo = False):
        """
        sets digital value. The mock driver emulates pressure transitions due to change in digital state.

        Parameters
        ----------
        number :: integer
            integer number that will be set to DI-4108 digital outputs
        echo :: boolean, optional
            optional flag that turn on reply.

        Returns
        -------

        Examples
        --------
        >>> mock.set_digital(number = 127)
        """
        from time import time
        before = self.sim_digital
        if 0<=number<=127:
            after = number
            self.sim_digital = number
            bin_array = self.parse_binary_number(value = after) - self.parse_binary_number(value = before)
            if bin_array[1] == -1 and self.sim_pressure_state != 0:
                self.sim_depre_event_trace = self.get_depre_trace()
                self.sim_depre_event_idx = 0
                self.sim_depre_event_flag = True
                self.sim_pressure_state = 0
            if bin_array[2] == -1 and self.sim_pressure_state != 1:
                self.sim_pre_event_trace = self.get_pre_trace()
                self.sim_pre_event_idx = 0
                self.sim_pre_event_flag = True
                self.sim_pressure_state = 1
            if bin_array[2] == 1:
                self.sim_slow_leak_start_time = time()
            if bin_array[1] == -1:
                sim_pump_event_flag = True
            elif bin_array[1] == 1:
                self.sim_pump_event_flag = False
        else:
            pass

        if echo == True:
            flag = True
        else:
            flag = False
        return flag

    def set_analog(self, echo = False, filterN = 1):
        flag = True
        if echo:
            flag = True
        return flag

    def set_acquisition_rate(self, rate = 1000, baserate = 20000, dec = 0, echo = True):
        """
        sets acquisition rate (simulation rate)

        Parameters
        ----------
        rate :: integer
            integer number that will be set to DI-4108 digital outputs
        baserate :: boolean, optional
            optional flag that turn on reply.
        dec :: integer

        Returns
        -------

        Examples
        --------
        >>> mock.set_acquisition_rate(rate = 1000, baserate = 20000, dec = 4)
        """
        self.sim_rate = int(1.0*baserate/dec)
        return True

    def start_scan(self):
        self.sim_flag = True
        info( 'The configured measurement(s) has(have) started')

    def stop_scan(self):
        self.sim_flag = False
        info("measurement ended")

    def full_stop(self):
        self.stop_scan()
        self.close_port()

    """Advance function"""
    def config_channels(self, rate = 3000, conf_digital = 127, set_digital = 127, dec = 20, baserate = 20000):
        x = self.config_digital(conf_digital, echo = True)
        a = self.set_digital(set_digital, echo = True)
        b = self.set_analog(echo = True)
        c = self.set_acquisition_rate(rate = rate, dec = dec, baserate = 20000, echo = True) #3000 gives maximum rate
        return x*a*b*c

    def get_readings(self, points_to_read = 1, to_read_analog = 8, to_read_digital = 1):
        """
        the original get_readings function should just return data from the buffer on the DI-4108 DATAQ. Since this is module is a mock device, there are extra functionality build in into this specific function. The function handles random number generation around specified values with specified standard deviations. The fucntion also includes what happens if pressurization and depresurrization event flags are True.
        """
        from numpy import zeros, random
        from time import time

        # first generate empty packets of specified dimensionality
        to_read = (int(to_read_analog)+int(to_read_digital)*2)
        res = zeros((to_read,points_to_read),dtype = 'int16')
        t1 = time()
        k=0
        for j in range(points_to_read):
            ###pump event handler
            if self.sim_pump_event_flag:
                if self.sim_pump_event_idx<len(self.sim_pump_event_trace):
                    self.sim_analog[0] = self.sim_pump_event_trace[self.sim_pump_event_idx]
                    self.sim_analog_std[0] = 1
                    self.sim_pump_event_idx +=1
                else:
                    self.sim_pump_event_flag = False
                    self.sim_analog_std[0] = 10
            else:
                flag = random.uniform(0,1) > self.pump_freq
                if flag:
                    self.sim_pump_event_idx = 0
                    self.sim_pump_event_trace = self.get_pump_trace()
                    self.sim_pump_event_flag = True
                else:
                    self.sim_pump_event_flag = False
            if self.sim_pre_event_flag:
                if self.sim_pre_event_idx<len(self.sim_pre_event_trace[5,:]):
                    self.sim_analog[5] = self.sim_pre_event_trace[5,self.sim_pre_event_idx]
                    self.sim_analog[6] = self.sim_pre_event_trace[6,self.sim_pre_event_idx]
                    self.sim_analog_std[5] = 1
                    self.sim_analog_std[6] = 1
                    self.sim_pre_event_idx +=1
                else:
                    self.sim_pre_event_flag = False
                    self.sim_analog_std[5] = 10
                    self.sim_analog_std[6] = 10
            if self.sim_depre_event_flag:
                if self.sim_depre_event_idx<len(self.sim_depre_event_trace[5,:]):
                    self.sim_analog[5] = self.sim_depre_event_trace[5,self.sim_depre_event_idx]
                    self.sim_analog[6] = self.sim_depre_event_trace[6,self.sim_depre_event_idx]
                    self.sim_analog_std[5] = 1
                    self.sim_analog_std[6] = 1
                    self.sim_depre_event_idx +=1
                else:
                    self.sim_depre_event_flag = False
                    self.sim_analog_std[5] = 10
                    self.sim_analog_std[6] = 10
            for i in [0,1,2,3,4,7]:
                res[i,j] = random.normal(self.sim_analog[i],self.sim_analog_std[i],1)[0]
            for i in [5,6]:
                res[i,j] = random.normal(self.sim_analog[i]*self.slow_leak(),self.sim_analog_std[i],1)[0]
            res[9,j] = self.sim_digital

            # this section simulates continous data generation. It will sleep for ~16 ms every 64 points.
            k+=1
            if k >= 64:
                sleep(64/self.sim_rate)
                k = 0
        flag = True
        return res.T, flag #(analog_data,digital_data)

    def blink(self):
        pass

# Supporting
    def get_pre_trace(self):
        print('get pre trace')
        from numpy import arange, zeros
        import random

        N = int(random.uniform(0,len(self.lst_pre)-1))
        spl_list = self.lst_pre[N]
        x = arange(0,333,1)*0.25
        data = zeros((10,333))

        data[5,:] = spl_list[5](x)
        var_first = spl_list[5](x[0])
        data[5,:] = data[5,:]-var_first
        val_last = data[5,-1]
        data[5,:] = data[5,:]*12000/val_last

        data[6,:] = spl_list[6](x)
        var_first = spl_list[6](x[0])
        data[6,:] = data[6,:]-var_first
        val_last = data[6,-1]
        data[6,:] = data[6,:]*12000/val_last
        return data

    def get_depre_trace(self):
        print('get depre trace')
        from numpy import arange, zeros
        import random

        N = int(random.uniform(0,len(self.lst_depre)-1))
        spl_list = self.lst_depre[N]
        x = arange(0,333,1)*0.25
        data = zeros((10,333))

        data[5,:] = spl_list[5](x)
        var_first = spl_list[5](x[-1])
        data[5,:] = data[5,:]-var_first
        val_last = data[5,0]
        data[5,:] = data[5,:]*12000/val_last

        data[6,:] = spl_list[6](x)
        var_first = spl_list[6](x[-1])
        data[6,:] = data[6,:]-var_first
        val_last = data[6,0]
        data[6,:] = data[6,:]*12000/val_last
        return data

    def get_pump_trace(self):
        print('get pump trace')
        from numpy import arange, zeros
        import random

        N = int(random.uniform(0,len(self.lst_pump)-1))
        spl_list = self.lst_pump[N]
        x = arange(0,333,1)*0.25
        data = spl_list(x)
        return data

########################################################
##### Artificial events
########################################################

    def pinhole_leak(self):
        """
        creates a pin hole leak event. Values in channel 5,6 are set to 0.

        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        >>> mock.pinhole_leak()
        """
        self.sim_analog[5] = 0
        self.sim_analog[6] = 0
        self.sim_pressure_state = 0

    def slow_leak(self):
        """
        emulates slow leak

        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        >>> mock.pinhole_leak()
        """
        def exp(t,amp,tau):
            from numpy import exp
            return exp(-t/tau)
        #self.sim_slow_leak_flag = flag
        #self.sim_slow_leak_tau = 1
        #self.sim_slow_leak_start_time = 0
        return exp(t = time()-self.sim_slow_leak_start_time, amp = 1, tau = self.sim_slow_leak_tau)


if __name__ == "__main__": #for testing
    import logging
    from tempfile import gettempdir
    driver = Driver()
    self = driver


    logging.basicConfig(filename=gettempdir()+'/DI_4108_BULK_LL.log',
                        level=logging.DEBUG, format="%(asctime)s %(levelname)s: %(message)s")
    print('self.self_test()')
    print('self.test1()')
    print('self.test2()')
    print('self.echo_test1()')
    print('self.performance_test1()')
    print('self.performance_test2()')
