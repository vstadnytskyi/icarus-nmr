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
    bit0_enable = pvproperty(value=1, dtype = int)
    bit1 = pvproperty(value=0, dtype = int)
    bit1_enable = pvproperty(value=1, dtype = int)
    bit2 = pvproperty(value=0, dtype = int)
    bit2_enable = pvproperty(value=1, dtype = int)
    bit3 = pvproperty(value=0, dtype = int)
    bit3_enable = pvproperty(value=0, dtype = int)
    bit4 = pvproperty(value=0, dtype = int)
    bit4_enable = pvproperty(value=0, dtype = int)
    bit5 = pvproperty(value=0, dtype = int)
    bit5_enable = pvproperty(value=0, dtype = int)
    bit6 = pvproperty(value=0, dtype = int)
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
                    new_val = io_dict[key]
                    cur_val = self.dio.value
                    print({ctime(time())},new_val,cur_val)
                    if new_val != cur_val:
                        await self.dio.write(val)
                        _bit0 = int(((val)&int(0b1))/(int(0b1)))
                        _bit1 = int(((val)&int(0b10))/(int(0b10)))
                        _bit2 = int(((val)&int(0b100))/(int(0b100)))
                        await self.bit0.write(_bit0)
                        await self.bit1.write(_bit1)
                        await self.bit2.write(_bit2)
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
        print({ctime(time())},'{}, new value {}'.format('dio putter',value))
        new_val = value
        cur_val = self.dio.value
        print({ctime(time())},new_val,cur_val)
        if new_val != cur_val:
            _bit0 = int(((value)&int(0b1))/(int(0b1)))
            _bit1 = int(((value)&int(0b10))/(int(0b10)))
            _bit2 = int(((value)&int(0b100))/(int(0b100)))
            await self.bit0.write(_bit0)
            await self.bit1.write(_bit1)
            await self.bit2.write(_bit2)
        return value
    @operating_mode.putter
    async def operating_mode(self, instance, value):
        print({ctime(time())},'Received update for the {}, sending new value {}'.format('operating_mode',value))
        self.trigger_mode = value
        if value == 0:
            await self.bit1_enable.write(1)
            await self.bit2_enable.write(1)
        elif value == 1:
            await self.bit1_enable.write(0)
            await self.bit2_enable.write(0)
        elif value == 2:
            await self.bit1_enable.write(0)
            await self.bit2_enable.write(0)

        return value
    @shutdown_state.putter
    async def shutdown_state(self, instance, value):
        print({ctime(time())},'Received update for the {}, sending new value {}'.format('shutdown_state',value))
        #self.device.set_DIO(value = value)
        return value
    @bit0.putter
    async def bit0(self, instance, value):
        print({ctime(time())},'Received update for the {}, sending new value {}'.format('bio0',value))
        cur_d = self.dio.value
        new_d = new_digital(cur_d,0,value)
        if new_d!=cur_d:
            self.device.set_dio(value = new_d)
        return value
        return value
    @bit0_enable.putter
    async def bit0_enable(self, instance, value):
        print({ctime(time())},'Received update for the {}, sending new value {}'.format('bio0_enable',value))
        #self.device.set_DIO(value = value)
        return value
    @bit1.putter
    async def bit1(self, instance, value):
        print({ctime(time())},'Received update for the {}, sending new value {}'.format('bio1',value))
        cur_d = self.dio.value
        new_d = new_digital(cur_d,1,value)
        if new_d!=cur_d:
            self.device.set_dio(value = new_d)
        return value
    @bit1_enable.putter
    async def bit1_enable(self, instance, value):
        print({ctime(time())},'Received update for the {}, sending new value {}'.format('bio1_enable',value))
        #self.device.set_DIO(value = value)
        return value
    @bit2.putter
    async def bit2(self, instance, value):
        print({ctime(time())},'Received update for the {}, sending new value {}'.format('bio2',value))
        cur_d = self.dio.value
        new_d = new_digital(cur_d,2,value)
        if new_d!=cur_d:
            self.device.set_dio(value = new_d)
        return value
    @bit2_enable.putter
    async def bit2_enable(self, instance, value):
        print({ctime(time())},'Received update for the {}, sending new value {}'.format('bio2_enable',value))
        #self.device.set_DIO(value = value)
        return value

    # @dio.getter
    # async def dio(self, instance):
    #     print(f"getter: {'dio'}, new value ")
    #     value = self.device.get_DIO()
    #     return value
    #
    # @data.getter
    # async def data(self, instance):
    #     value = self.device.queue.dequeue(self.device.pr_packet_size).flatten()
    #     if value.shape[0] > 1280:
    #         print(f'{value.shape}')
    #         print(f"getter: {'data'}, queue length {self.device.queue.length}")
    #         print(f"getter: {'data'}, queue rear {self.device.queue.rear}")
    #     return value
    #
    # @peek_data.getter
    # async def peek_data(self, instance):
    #     value = self.device.queue.peek_first_N(N=6400).flatten()
    #     return value
    #
    # @queue_length.startup
    # async def queue_length(self, instance, async_lib):
    #     await self.queue_length.write(self.device.queue.length)
    # @queue_length.getter
    # async def queue_length(self, instance):
    #     print(f"getter: {'data'}, queue length {self.device.queue.length}")
    #     value = self.device.queue.length
    #     return value

    # @ai_offset.startup
    # async def ai_offset(self, instance, async_lib):
    #     await self.ai_offset.write(self.device.pressure_sensor_offset)
    # @ai_offset.putter
    # async def ai_offset(self, instance, value):
    #     print(f"Received update for the {'dio'}, sending new value {value}")
    #     self.device.pressure_sensor_offset = value
    #     return value
    # @ai_offset.getter
    # async def ai_offset(self, instance):
    #     print(f"getter: {'ai_offset'}, new value ")
    #     value = self.device.pressure_sensor_offset
    #     return value

def int_to_binary(value):
    return bin(value+128)[-7:][::-1]

def new_digital(old_digital, bit, new_bit_value):
    """

    """
    def int_to_binary(value):
        return bin(value+128)[-7:][::-1]

    from numpy import sign
    old_bit_value = int(int_to_binary(old_digital)[bit])
    bit_diff = new_bit_value - old_bit_value
    new_digital = old_digital + sign(bit_diff)*(2**bit)
    return new_digital

if __name__ == '__main__':

    ioc_options, run_options = ioc_arg_parser(
        default_prefix='digital_handler_mock:',
        desc=dedent(Server.__doc__))
    ioc = Server(**ioc_options)


    ioc.device = device
    run(ioc.pvdb, **run_options)
