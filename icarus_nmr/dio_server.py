"""

Digital Input and Output handler server

"""
from caproto.server import pvproperty, PVGroup, ioc_arg_parser, run
import caproto
from textwrap import dedent
from pdb import pm

from numpy import random, array, zeros, ndarray, nan, isnan
from time import time, sleep, ctime

arr_shape = (64,10)
class Server(PVGroup):
    """
    An IOC with three uncoupled read/writable PVs

    Scalar PVs
    ----------
    CPU
    MEMORY
    BATTERY

    Vectors PVs
    -----------

    """

    dio = pvproperty(value=127, dtype = int)

    bit0 = pvproperty(value=0, dtype = int)
    bit0_indicator = pvproperty(value="na", dtype = str)
    bit0_enable = pvproperty(value=1, dtype = int)

    bit1 = pvproperty(value=0, dtype = int)
    bit1_indicator = pvproperty(value='na', dtype = str)
    bit1_enable = pvproperty(value=1, dtype = int)

    bit2 = pvproperty(value=0, dtype = int)
    bit2_indicator = pvproperty(value='na', dtype = str)
    bit2_enable = pvproperty(value=1, dtype = int)

    bit3 = pvproperty(value=0, dtype = int)
    bit3_indicator = pvproperty(value='na', dtype = str)
    bit3_enable = pvproperty(value=0, dtype = int)

    bit4 = pvproperty(value=0, dtype = int)
    bit4_indicator = pvproperty(value='na', dtype = str)
    bit4_enable = pvproperty(value=0, dtype = int)

    bit5 = pvproperty(value=0, dtype = int)
    bit5_indicator = pvproperty(value='na', dtype = str)
    bit5_enable = pvproperty(value=0, dtype = int)

    bit6 = pvproperty(value=0, dtype = int)
    bit6_indicator = pvproperty(value='na', dtype = str)
    bit6_enable = pvproperty(value=0, dtype = int)

    shutdown_state = pvproperty(value=0, dtype = int)

    operating_mode = pvproperty(value=0,dtype=int)


    pulse_generator_depre_width = pvproperty(value=0.1, dtype = float)
    pulse_generator_pre_width = pvproperty(value=0.1, dtype = float)
    pulse_generator_delay = pvproperty(value=0.1, dtype = float)
    pulse_generator_period = pvproperty(value=0.1, dtype = float)

    @dio.startup
    async def dio(self, instance, async_lib):
        # This method will be called when the server starts up.
        self.io_pull_queue = async_lib.ThreadsafeQueue()
        self.io_push_queue = async_lib.ThreadsafeQueue()
        try:
            self.device.io_push_queue = self.io_push_queue
            self.device.io_pull_queue = self.io_pull_queue
        except:
            pass

        # Loop and grab items from the response queue one at a time
        while True:
            io_dict = await self.io_push_queue.async_get()
            # Propagate the keypress to the EPICS PV, triggering any monitors
            # along the way
            print({ctime(time())},f'inside server while True loop: {io_dict}')
            for key in list(io_dict.keys()):
                if key == 'dio':
                    print('dio arrived from server')
                elif key == 'bit0':
                    await self.bit0.write(io_dict[key])
                elif key == 'bit0_enable':
                    await self.bit0_enable.write(io_dict[key])
                elif key == 'bit1':
                    await self.bit1.write(io_dict[key])
                elif key == 'bit1_enable':
                    await self.bit1_enable.write(io_dict[key])
                elif key == 'bit2':
                    await self.bit2.write(io_dict[key])
                elif key == 'bit2_enable':
                    await self.bit2_enable.write(io_dict[key])
                elif key == 'bit3':
                    await self.bit3.write(io_dict[key])
                elif key == 'bit3_enable':
                    await self.bit3_enable.write(io_dict[key])
                elif key == 'bit4':
                    await self.bit4.write(io_dict[key])
                elif key == 'bit4_enable':
                    await self.bit4_enable.write(io_dict[key])
                elif key == 'bit5':
                    await self.bit5.write(io_dict[key])
                elif key == 'bit5_enable':
                    await self.bit5_enable.write(io_dict[key])
                elif key == 'bit6':
                    await self.bit6.write(io_dict[key])
                elif key == 'bit6_enable':
                    await self.bit6_enable.write(io_dict[key])


    @dio.putter
    async def dio(self, instance, value):
        """
        when the dio PV is changed in the database it submits new value to the core module. All smarts are in the core module
        """
        echo = True
        print(f'{ctime(time())}: {"dio putter"}, new value {value}')

        print(f'{ctime(time())} operational mode is {self.operating_mode.value}')

        print(f'{ctime(time())} dio value is {self.dio.value}')

        arr = int_to_binary(value)
        if echo: print(f'arr = {arr}')

        modes = ['manual','pulsed','console']
        current_mode = modes[self.operating_mode.value]
        if current_mode is 'manual':
            print(f'current operational mode is {current_mode}')
        elif current_mode is 'pulsed':
            print(f'current operational mode is {current_mode}')
        elif current_mode is 'console':
            print(f'current operational mode is {current_mode}')

        #Update indicators of digital state. Does not trigger update of buttons.
        bit0 = int(arr[0])
        if echo: print(f'bit0 = {bit0}')
        await self.bit0_indicator.write(str(bit0))

        bit1 = int(arr[1])
        if echo: print(f'bit1 = {bit1}')
        await self.bit1_indicator.write(str(bit1))

        bit2 = int(arr[2] )
        if echo: print(f'bit2 = {bit2}')
        await self.bit2_indicator.write(str(bit2))

        bit3 = int(arr[3])
        if echo: print(f'bit3 = {bit3}')
        await self.bit3_indicator.write(str(bit3))

        bit4 = int(arr[4])
        if echo: print(f'bit4 = {bit4}')
        await self.bit4_indicator.write(str(bit4))

        bit5 = int(arr[5])
        if echo: print(f'bit5 = {bit5}')
        await self.bit5_indicator.write(str(bit5))

        bit6 = int(arr[6])
        if echo: print(f'bit6 = {bit6}')
        await self.bit6_indicator.write(str(bit6))

    @operating_mode.putter
    async def operating_mode(self, instance, value):
        print({ctime(time())},'Received update for the {}, sending new value {}'.format('operating_mode',value))
        self.device.set_trigger_mode(value)
    @operating_mode.getter
    async def operating_mode(self, instance):
        print(f'{ctime(time())} operating mode getter')

    @shutdown_state.putter
    async def shutdown_state(self, instance, value):
        print({ctime(time())},'Received update for the {}, sending new value {}'.format('shutdown_state',value))
        self.device.set_operating_mode(value = value)

    @bit0.putter
    async def bit0(self, instance, value):
        print({ctime(time())},'Received update for the {}, sending new value {}'.format('bio0',value))
        if self.bit0.value != value:
            print(f'True current bit0 is {self.bit0.value } and new value is {value}')
            current_dio = self.dio.value
            self.device.set_bit(current_dio, bit = 0, value = value)
        else:
            print(f'False current bit0 is {self.bit0.value } and new value is {value}')
        return value
    @bit0_enable.putter
    async def bit0_enable(self, instance, value):
        print(f'{ctime(time())} Received update for the {"bio0_enable"}, sending new value {value}')
        #self.device.set_DIO(value = value)
        return value

    @bit1.putter
    async def bit1(self, instance, value):
        print({ctime(time())},'Received update for the {}, sending new value {}'.format('bio0',value))
        if self.bit1.value != value:
            print(f'True current bit0 is {self.bit1.value } and new value is {value}')
            current_dio = self.dio.value
            self.device.set_bit(current_dio, bit = 1, value = value)
        else:
            print(f'False current bit1 is {self.bit1.value } and new value is {value}')
        return value
    @bit1_enable.putter
    async def bit1_enable(self, instance, value):
        print(f'{ctime(time())} Received update for the {"bio1_enable"}, sending new value {value}')
        #self.device.set_DIO(value = value)
        return value
    @bit2.putter
    async def bit2(self, instance, value):
        print({ctime(time())},'Received update for the {}, sending new value {}'.format('bio2',value))
        if self.bit2.value != value:
            print(f'True current bit2 is {self.bit2.value } and new value is {value}')
            current_dio = self.dio.value
            self.device.set_bit(current_dio, bit = 2, value = value)
        else:
            print(f'False current bit2 is {self.bit2.value } and new value is {value}')
        return value
    @bit2_enable.putter
    async def bit2_enable(self, instance, value):
        print({ctime(time())},'Received update for the {}, sending new value {}'.format('bio2_enable',value))
        #self.device.set_DIO(value = value)
        return value

#
#
def int_to_binary(value):
    return bin(value+128)[-7:][::-1]
#
# def new_digital(old_digital, bit, new_bit_value):
#     """
#
#     """
#     def int_to_binary(value):
#         return bin(value+128)[-7:][::-1]
#
#     from numpy import sign
#     old_bit_value = int(int_to_binary(old_digital)[bit])
#     bit_diff = new_bit_value - old_bit_value
#     new_digital = old_digital + sign(bit_diff)*(2**bit)
#     return new_digital

if __name__ == '__main__':

    ioc_options, run_options = ioc_arg_parser(
        default_prefix='digital_handler_mock:',
        desc=dedent(Server.__doc__))
    ioc = Server(**ioc_options)


    ioc.device = device
    run(ioc.pvdb, **run_options)
