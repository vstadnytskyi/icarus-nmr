"""
DATAQ 4108 driver level code
author: Valentyn Stadnytskyi
June 2018 - June 2018

1.0.0 - designed for usb Bulk protocol.
1.0.1 - dec is added to the communication

"""

from numpy import nan, mean, std, asarray, array, concatenate, delete, round, vstack, hstack, zeros, transpose, split
from serial import Serial
from time import time, sleep, clock
import sys
import os.path
import struct
from pdb import pm
from time import gmtime, strftime
import logging

from struct import pack, unpack
from timeit import Timer
from logging import info,warn, debug, error
import traceback
__version__ = '1.0.1'

class Driver(object):

    def __init__(self):
        #tested dec 17, 2017
        self.available_ports = []
        self.dev = None

    def init(self):
        self.discover()
        self.use_port()

        info("initialization of the driver is complete")

    def get_information(self):
        if self.dev != None:
            self.dev_dict = {}
            self.epi_dict = {}
            self.dev_dict['DEV:address'] = self.dev.address
            self.dev_dict['DEV:bDeviceClass'] = self.dev.bDeviceClass
            self.dev_dict['DEV:bDescriptorType'] = self.dev.bDescriptorType
            self.dev_dict['DEV:bDeviceProtocol'] = self.dev.bDeviceProtocol
            self.dev_dict['DEV:bLength'] = self.dev.bLength
            self.dev_dict['DEV:bMaxPacketSize0'] = self.dev.bMaxPacketSize0
            self.dev_dict['DEV:bNumConfigurations'] = self.dev.bNumConfigurations
            self.dev_dict['DEV:manufacturer'] = self.dev.manufacturer
            self.dev_dict['DEV:serial_number'] = self.dev.serial_number
            self.dev_dict['DEV:speed'] = self.dev.speed
            self.dev_dict['DEV:product'] = self.dev.product

            #endpoint IN description
            self.epi_dict['EPI:bmAttributes'] = self.epi.bmAttributes
            self.epi_dict['EPI:wMaxPacketSize'] = self.epi.wMaxPacketSize
            self.epi_dict['EPI:bSynchAddress'] = self.epi.bSynchAddress
            self.epi_dict['EPI:bInterval'] = self.epi.bInterval
            self.epi_dict['EPI:bEndpointAddress'] = self.epi.bEndpointAddress
            self.epi_dict['EPI:bDescriptorType'] = self.epi.bDescriptorType
            self.epi_dict['EPI:bInterval'] = self.epi.bInterval
            self.epi_dict['EPI:bInterval'] = self.epi.bInterval

    def get_hardware_information(self):
        dic = {}
        dic[b'Device name'] = self.inquire(b'info 1 \r').split(b'info 1 ')[1][1:-1]
        dic[b'Firmware version'] = self.inquire(b'info 2 \r').split(b'info 2 ')[1][1:-1]
        dic[b'Serial Number'] = self.inquire(b'info 6 \r').split(b'info 6 ')[1][1:-1]
        dic[b'Sample Rate Divisor'] = self.inquire(b'info 9 \r').split(b'info 9 ')[1][1:-1]

        return dic

    def use_port(self, port = ''):
        import usb.core
        import usb.util


        self.dev.reset()

        # set the active configuration. With no arguments, the first
        # configuration will be the active one
        self.dev.set_configuration()

        # get an endpoint instance
        cfg = self.dev.get_active_configuration()
        intf = cfg[(0,0)]

        self.epo = usb.util.find_descriptor(
                                      intf,
                                      # match the first OUT endpoint
                                      custom_match = \
                                      lambda e: \
                                      usb.util.endpoint_direction(e.bEndpointAddress) == \
                                      usb.util.ENDPOINT_OUT)

        self.epi = usb.util.find_descriptor(
                                      intf,
                                      # match the first IN endpoint
                                      custom_match = \
                                      lambda e: \
                                      usb.util.endpoint_direction(e.bEndpointAddress) == \
                                      usb.util.ENDPOINT_IN)

        assert self.epo is not None
        assert self.epi is not None
        self.epi.wMaxPacketSize = 7200000
        self.epo.wMaxPacketSize = 7200000
        self.epi.bmAttributes = 1
        self.epi.bInterval = 100
        self.usb_buff = int(self.epi.wMaxPacketSize/100)
        #self.readall()

    def discover(self):
        """
        the function allows to discover DI-4108 device.
        returns: flag if a device(devices) are found.
        assigns: self.available_ports list entry
        [0] - COM port namer
        pvproperty(value=2.0)[1] - serial number
        """
        import usb.core
        flag = True
        self.dev = usb.core.find(idVendor=0x0683, idProduct=0x4108)
        if self.dev is None:
            raise ValueError('Device not found')
            flag = False
        return flag

    """Basic serial communication functions"""

    def read(self,N = 0):
        if N == 0:
            usb_buff = int(self.usb_buff)
        else:
            usb_buff = int(N)
        from time import sleep
        #tested dec 17, 2017
        string = b""
        timeout = 1000
        try:
            data = self.dev.read(self.epi,usb_buff,timeout)
        except:
            error(traceback.format_exc())
            data = ''

        if len(data) != 0:
            for i in data:
                string += bytes([i])
        return string

    def readall(self):
        return self.read(0)

    def write(self,command):
        try:
            self.dev.write(self.epo,command)
        except:
            error(traceback.format_exc())

    def inquire(self,command):
        self.write(command)
        res = self.read(self.usb_buff)
        return res

    def close_port(self):
        pass
    """DI-4108 Communcation functions"""

    def config_digital(self, number = 127, echo = False):
        #tested dec 17, 2017
        string = 'endo ' + str(number) + '\r'
        flag = False
        self.write(string)
        a = self.readall()
        info('%r' % a)
        if echo == True:
            if a == 'endo ' + str(number) + '\r':
                flag = True
            else:
                flag = False
        else:
            flag = None
        return flag

    def set_digital(self, number = 127, echo = False):
        #tested dec 17, 2017
        string = 'dout ' + str(number) + ' \r'
        flag = False
        self.write(string)
        if echo == True:
            a = self.readall()
            debug('%r' % a)
            if a == 'dout ' + str(number) + ' \r\x00':
                flag = True
            else:
                flag = False
        else:
            flag = None
        return flag

    def set_analog(self, echo = False, filterN = 1):
        #tested dec 17, 2017
        import traceback
        flag = False
        try:
            filterN = int(filterN)
        except:
            error(traceback.format_exc())
            filterN = 1

        self.write('filter * '+str(int(filterN))+' \r')
        # 0 - Sets all channels to read the last point; 1 - CIC filter
        self.write('slist 0 0 \r') # 256 Sets analog channel 0 to be read at +-5V, increment by 1 to go to next channel
        self.write('slist 1 1 \r') # 257 "" but channel 1
        self.write('slist 2 2 \r') # 1282 Sets to read channel 2 at +-.2V
        self.write('slist 3 3 \r') # Sets to read channel 3 at +-.2V
        self.write('slist 4 4 \r') # Sets to read channel 4 at +-.2V
        self.write('slist 5 5 \r') # Sets to read channel 5 at +-.2V
        self.write('slist 6 6 \r') # Sets to read channel 6 at +-5V
        self.write('slist 7 7 \r') # Sets to read channel 7 at +-5V
        self.write('slist 8 8 \r') # Sets to read digital input
        self.write('ps 6 \r') # set DATSQ packet size 1024 bytes page 3 di-4x08 Protocol

        #read buffer. The echoed commands need to be checked for succesful inplementation.
        #the following part was supposed to check if command has echoed back, meaning was received by the DI-4018.
        #I don't think this command is needed at all.
        a = self.readall()
        b = self.readall()
        #print('%r' % (a + b))
        if echo == True:
            if (a+b) == 'filter * 0 \r\x00slist 0 256 \rslist 1 257 \rslist 2 1282 \r\x00slist 3 1283 \r\x00slist 4 1284 \r\x00slist 5 1285 \r\x00slist 6 262 \rslist 7 263 \rslist 8 8 \r':
                flag = True
        else:
            flag = True
        return flag

    def set_acquisition_rate(self, rate = 1000, baserate = 20000, dec = 0, echo = True):
        #tested dec 17, 2017
        baserate = 20000
        if dec == 0:
            dec = int(baserate/rate)

        flag = False
        string = 'srate ' + str(int(60000000/baserate)) +' \r'
        #self.ser.write('srate 6000000\r') # Supposedly sets it to read at 50kHz, Hz=60000000/srate
        self.write(string)
        string = 'dec ' + str(dec) +' \r'
        self.write(string)
        from time import sleep
        sleep(0.2)

        #print('%r,%r' % (a,b))
        if echo == True:
            a = self.readall()
            debug(a)
            b = self.readall()
            debug(a)
            if a+b == 'srate '+ str(60000000/rate)+ '\r\x00':
                flag = True
        else:
            flag = True
        return flag

    def start_scan(self):
        info( self.write('start\r'))
        info( 'The configured measurement(s) has(have) started')

    def stop_scan(self):
        self.write('stop\r')
        info("measurement ended")

    def full_stop(self):
        self.stop_scan()
        self.close_port()

    def flush(self):
        """backcompetability with serial communication"""
        pass

    """Advance function"""
    def config_channels(self, rate = 3000, conf_digital = 127, set_digital = 127, dec = 20, baserate = 20000):
        x = self.config_digital(conf_digital, echo = True)
        a = self.set_digital(set_digital, echo = True)
        b = self.set_analog(echo = True)
        c = self.set_acquisition_rate(rate = rate, dec = dec, baserate = 20000, echo = True) #3000 gives maximum rate
        return x*a*b*c

    def get_readings(self, points_to_read = 1, to_read_analog = 8, to_read_digital = 1):
        to_read = int(to_read_analog)*2+int(to_read_digital)*2
        result = self.read(to_read*points_to_read)
        if b'stop' in result:
            flag = False
        else:
            flag = True
        try:

            data = asarray(unpack(('h'*to_read_analog+'BB')*points_to_read,result))
        except:
            error(traceback.format_exc())
            data = None



            #analog_data = asarray(unpack('h'*to_read_analog,res[0:to_read_analog*2])) #this will be
        #first N bytes (where N/2 is number of analog channels to read
        #see https://docs.python.org/2/library/struct.html for 'h' description
            #digital_data = array(unpack('B',res[-1:])[0])
        #This how we can format the integer to binary string ---->> bin(unpack('B',res[-1])[0])[2:].zfill(7).split()
        #this will unpack the very last byte as binary and make sure to
        #keep the leading zero. The very first zero 'D7' byte count 18 (see manual) is ommited.
        #will be shown as a string. We need to convert it to a numpy array for easier usage
        try:
            res = transpose(asarray(split(data,points_to_read)))
        except:
            error(traceback.format_exc())
            res = None
        return res, flag #(analog_data,digital_data)

    def blink(self):
        from time import sleep
        for i in range(8):
            self.write('led ' + str(i) + ' \r')
            sleep(1)
        self.write('led ' + str(7) + ' \r')


    """Test functions"""
    def self_test(self):
        self.inquire('led 7\r')
        self.tau = 0.001
        #dictionary with device parameters such as S\N, device name, ect
        self.dict = {}
        self.dict['Device name'] = self.inquire('info 1 \r').split('info 1 ')[1][1:-1]
        self.dict['Firmware version'] = self.inquire('info 2 \r').split('info 2 ')[1][1:-1]
        self.dict['Serial Number'] = self.inquire('info 6 \r').split('info 6 ')[1][1:-1]
        self.dict['Sample Rate Divisor'] = self.inquire('info 9 \r').split('info 9 ')[1][1:-1]
        #Useful variables
        #wait time after write (before) read. This seems to be not necessary.
        for i in self.dict.keys():
            print('%r, %r' % (i, self.dict[i]))
        print('information request complete: the DI-4108 with SN %r' %self.dict['Serial Number'])
        print('%r' % self.inquire('led 2\r'))

    def test1(self):
        self.self_test()
        self.config_channels()

        self.start_scan()
        while self._waiting()[0] <1:
            sleep(0.001)
        start_t = time()
        while time()-start_t<2:
            print("%0.5f %r %r" % (time()-start_t,self._waiting()[0],self.get_readings()))
        self.stop_scan()
        print('test 1 is Done. IN buffer has all data')
        print('data = dev.get_readings()')
        print('buffer waiting %r' % self._waiting()[0])

    def test2(self):
        self.self_test()
        self.config_channels()
        self.start_scan()
        sleep(6)
        self.stop_scan()
        sleep(1)
        while self._waiting()[0]>5:
            print('time %r and value %r'% (time(),self.get_readings()))
        print('test 2 is Done')

    def test3(self):
        self.self_test()
        self.config_channels()
        self.start_scan()
        sleep(6)
        self.stop_scan()
        print(self.waiting())
        sleep(1)
        while self.waiting()[0]>5:
            print(self.waiting()[0])
            print(self.get_readings())
        print('test 2 is Done')


    def echo_test1(self):
        self.config_channels()
        self.start_scan()
        while self.waiting()[0] <1:
            sleep(0.001)
        start_t = time()
        while time()- start_t <1:
            self.write('dout 0\r')
            self.write('dout 127 \r')
            sleep(0.06)
        self.stop_scan()
        print("%r" % self._waiting()[0])
        data = self.readall()
        print('%r' % data)

    def performance_test1(self):
        self.self_test()
        self.config_channels()

        self.start_scan()
        while self.waiting()[0] <10000:
            sleep(0.001)
        start_t = time()
        self.stop_scan()

        print('test 1 is Done. IN buffer has all data')
        print('data = dev.get_readings(10)')
        print('buffer waiting %r' % self._waiting()[0])
        print('t = Timer(lambda: dev.get_readings(N))')
        print('print t.timeit(number = M)')

    def performance_test2(self):
        self.self_test()
        self.config_channels()

        self.start_scan()
        start_t = time()
        self.lst = []
        time_st = time()
        while time()-start_t<10:
            if self._waiting()[0]> 512*16:
                data = self.get_readings(512)
                self.lst.append([time()-start_t,self._waiting()[0],(time() - time_st)*1000])
                print("%r %0.10f" % (self._waiting()[0], (time() - time_st)*1000))
            sleep(24/1000) #wait for 12.8 ms
        start_t = time()
        self.stop_scan()
        print('time between 4 kS = %0.5f' % mean(10.0/len(self.lst)))
        print('Sampling rate: %0.1f' % (512/mean(10.0/len(self.lst))))
        print('test 1 is Done. IN buffer has all data')
        print('data = dev.get_readings(10)')
        print('buffer waiting %r' % self._waiting()[0])
        print('t = Timer(lambda: dev.get_readings(N))')
        print('print t.timeit(number = M)')

driver = Driver()

if __name__ == "__main__": #for testing
    import logging
    from tempfile import gettempdir
    self = driver


    logging.basicConfig(#filename=gettempdir()+'/DI_4108_BULK_LL.log',
                        level=logging.DEBUG, format="%(asctime)s %(levelname)s: %(message)s")
    print('self.self_test()')
    print('self.test1()')
    print('self.test2()')
    print('self.echo_test1()')
    print('self.performance_test1()')
    print('self.performance_test2()')
