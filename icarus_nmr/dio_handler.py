#!/bin/env python
"""
The Event Detector LL for the High Pressure Apparatus
author: Valentyn Stadnytskyi
dates: June 09 2018 - November 16 2018
"""

class Handler():

    bit_HPpump = 0b1
    bit_valve1 = 0b10
    bit_valve2 = 0b100
    bit_valve3 = 0b1000
    bit_log = 0b10000
    flag_play_sequence = False
    sequence_string = 'i4L,i1L,w_150_ms,i1H,w_300_ms,i2L,w_30_ms,i2H,w_100_ms,i3L,w_500_ms,i3H,w_2_s'
    pr_pulse_generator_counter = 0


    def __init__(self, client):
        """
        """
        self.name = 'PulseGenerator'
        self.client = client
        self.running = False
        self.console_running = False

        self.io_push_queue = None
        self.io_put_queue = None

    def init(self):
        """
        initialization functions. sets instance to default values.

        Parameters
        ----------

        Returns
        -------

        Examples
        --------
        >>> pulse_generator.init()
        """
        from numpy import nan
        self.trigger_mode = 2 # 0 - manual, 1 - pulsed, 2 - console. Always start with concole

        self.running = False

        #self.curr_DIO = int('1111111',2)


    def set_dio(self, value):
        """
        a wrapper to set digital state in the device handler process via channel access

        Parameters
        ----------
        value :: integer

        Returns
        -------

        Examples
        --------
        >>> value = client.get_dio()
        """

        self.client.set_dio(value)


    def get_dio(self):
        """
        a wrapper to get digital state in the device handler process via channel access

        Parameters
        ----------

        Returns
        -------
        value :: integer

        Examples
        --------
        >>> value = self.client.get_dio()
        """

        value = self.client.get_dio()

        return value


    def pulse(self, current_dio, valve = 1, duration = 1, precision = False, echo = False):
        """
        generates a negative pulse (high-low-high) for 'duration' seconds for 'valve' (bit)

        Parameters
        ----------
        current_dio :: int
        valve :: int
        duration :: float
        precision :: boolean
        echo :: boolean

        Returns
        -------

        Examples
        --------
        >>> self.pulse(valve = 1, duration = 1)
        """
        from time import sleep
        if valve == 1:
            valve_bit = int(self.bit_valve1) # Depressure
        elif valve == 2:
            valve_bit = int(self.bit_valve2) # Pressure
        elif valve == 3:
            valve_bit = int(self.bit_valve3) # Bit 3
        elif valve == 0:
            valve_bit = int(self.bit_HPpump) # High pressure valve
        elif valve == -1:
            valve_bit = int('0000000',2) # Wait
        else:
            valve_bit = int('0000000',2) # Wait if valve selection is not recognized
        curr_DIO = current_dio
        new_DIO = curr_DIO-valve_bit
        if valve_bit != 0:
            self.set_dio(new_DIO) #down
        if precision:
            precision_sleep.psleep(duration)
        else:
            sleep(duration)
        if valve_bit != 0:
            self.set_dio(curr_DIO) # up
        print('DIO %r -> %r -> %r' % (curr_DIO,new_DIO,curr_DIO))


    def set_bit(self, current_dio, bit = 1, value = 1):
        """
        sets bit 'bit' to value 'value' (0 or 1)

        Parameters
        ----------
        bit :: int
        valve :: int

        Returns
        -------

        Examples
        --------
        >>> self.set_bit(bit = 1, value = 1)
        """
        from time import sleep
        if bit == 1:
            _bit = int(self.bit_valve1) # Depressure
        elif bit == 2:
            _bit = int(self.bit_valve2) # Pressure
        elif bit == 3:
            _bit = int(self.bit_valve3) # Bit 3
        elif bit == 0:
            _bit = int(self.bit_HPpump) # High pressure valve
        elif bit == -1:
            _bit = int('0000000',2) # Wait
        else:
            _bit = int('0000000',2) # Wait if valve selection is not recognized
        curr_DIO = current_dio
        new_DIO = curr_DIO-_bit

        self.set_dio(new_DIO) #down
        print('setting bit %r -> %r -> %r' % (curr_DIO,new_DIO))

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

    def start(self):
        """
        for back competibility with older SL codes does nothing
        """
        from ubcs_auxiliary.threading import new_thread
        if not self.running:
            new_thread(self.run)

    def stop(self):
        self.set_DIO(self.default_state)
        self.running = False

    def close(self):
        self.stop()

    def run_once(self):
        """
        """
        from icarus_nmr.event_detector import event_detector
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
                self.DIO = self.DIO_default
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

    def run(self):
        """
        the while True loop with pulse generator.
        it has to run all the time for high pressure pump pulse to
        be generated properly.
        important parameters: trigger: 0 manual, 1 -internal; 2 - external
        """
        from time import clock, time


        #preparation of the while true loop
        self.set_DIO(self.object.ctrls.DIO_default)
        sleep(0.3)
        self.curr_DIO  = self.get_DIO()
        self.running = True
        self.paused = False
        self.meas = {}
        self.meas['period'] = self.period
        manual_flag = True
        self.console_counter = 0
        self.update_period = 0.5

        #While true loop for the device
        while self.running:
            self.run_once()





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
        return self.object.ctrls.pg_period
    def set_period(self,value = 0):
        self.object.ctrls.pg_period = value
    period = property(get_period,set_period)

    def get_tw1(self):
        return self.object.ctrls.pg_depre_pulse_width
    def set_tw1(self,value = 0):
        self.object.ctrls.pg_depre_pulse_width = value
    tw1 = property(get_tw1,set_tw1)

    def get_tw2(self):
        return self.object.ctrls.pg_pre_pulse_width
    def set_tw2(self,value = 0):
        self.object.ctrls.pg_pre_pulse_width = value
    tw2 = property(get_tw2,set_tw2)

    def get_td(self):
        return self.object.ctrls.pg_delay_width
    def set_td(self,value = 0):
        self.object.ctrls.pg_delay_width = value
    td = property(get_td,set_td)

    def get_safe_state(self):
        return self.object.ctrls.safe_state
    def set_safe_state(self,value = 0):
        self.object.ctrls.safe_state = value
    safe_state = property(get_safe_state,set_safe_state)




    def get_trigger_mode(self):
        """
        returns trigger mode from pulse_generator instance
        """
        return self.object.ctrls.trigger_mode
    def set_trigger_mode(self,value = ''):
        """
        sets trigger mode either from CA monitor or manually via value variable
        """
        value = int(value)
        if value == 0 or value == 1 or value == 2 or value == 3:
            curr_trigger_mode = self.trigger_mode
            self.object.ctrls.trigger_mode = value
    trigger_mode = property(get_trigger_mode,set_trigger_mode)








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
