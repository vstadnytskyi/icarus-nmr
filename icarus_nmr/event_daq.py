
import sys
if sys.version_info[0] == 3:
    if sys.version_info[1] <= 7:
        from time import gmtime, strftime, time, sleep, clock
    else:
        from time import gmtime, strftime, time, sleep
        from time import perf_counter as clock
else:
    from time import gmtime, strftime, time, sleep, clock

from logging import debug, info, warning, error

from numpy import nan

sys.path.append('/Users/femto-13/All-Projects-on-femto/LaserLab/Software/')

class DAQ(object):
    freq = nan
    running = False
    def __init__(self, client):
        self.buffer_shape = (25600, 10)
        self.client = client

    def init(self):
        """
        initialize class, create all necessary varibles and isntances.
        """
        from circular_buffer_numpy.circular_buffer import CircularBuffer
        client = self.client
        self.circular_buffer = CircularBuffer(shape = self.buffer_shape, dtype = 'int16')
        self.packet_shape = client.packet_shape.read().data
        self.packet_length = self.packet_shape[0]
        self.freq = int(client.freq.read().data[0])
        self.packet_buffer_length = int(self.buffer_shape[0]/self.packet_length)
        self.start_time = None
        self.threads = {}


    def start(self):
        """
        start function self.run in new thread
        """
        # use auxiliary library new_thread wrapper
        # create new thread with self.run
        # add the thread pointer to self.threads for further inspection
        from ubcs_auxiliary.threading import new_thread
        self.threads['running'] = new_thread(self.run,)

    def stop(self):
        """
        stop function self.run that is running in a separate thread
        """
        self.running = False

    def run_once(self):
        """
        execute code for while True loop once
        """
        from time import time
        data = self.get_data()
        if self.start_time == None:
            self.start_time = time() - data.shape[1]/self.freq

        self.circular_buffer.append(data)
        self.packet_pointer = int(((self.circular_buffer.pointer+1)/self.packet_length)-1)
        self.g_packet_pointer = int(((self.circular_buffer.g_pointer+1)/self.packet_length)-1)

    def get_data(self):
        """
        return data from DAQ server via a client class
        """
        # if the queue on device side is shorter than 128, wait
        # read on packet of data from the client
        # return acquire data
        from time import sleep
        client = self.client
        while client.queue_length.read().data < 128:
            sleep(0.1)
        data = client.data.read().data.reshape((self.packet_shape))
        return data

    def run(self):
        """
        execute run_once function in a while self.running loop indefinitely.
        """
        from time import sleep
        self.running = True
        while self.running:
            self.run_once()

    def get_packet_ij(self,i,j): #return from i to j
        """
        return data from circular buffer between packets i and j
        """
        from numpy import nan
        length = self.circular_buffer.shape[0]
        while i > length:
            i-= length
        while j > length:
            j-= length

        if j >= i:
            debug(i,j)
            result = self.circular_buffer.get_N((j-i+1)*self.packet_length,(j+1)*self.packet_length-1)
        else:
            result = nan
        return result

    def get_ring_buffer_N(self,N,pointer):
        """
        return N entries before pointer from circular buffer
        """
        while pointer >= (self.circular_buffer.shape[0]):
            pointer = int(pointer - self.circular_buffer.shape[0])
        res = self.circular_buffer.get_N(N, pointer)
        return res

if __name__ == '__main__':
    import socket
    SERVER_NAME = socket.gethostname()
    from icarus_nmr.event_daq import DAQ

    from icarus_nmr.event_client import Client


    client = Client(device_ca_server_prefix = f'device_{SERVER_NAME}:',dio_ca_server_prefix = f'dio_{SERVER_NAME}:')
    daq = DAQ(client)
    daq.init()
    daq.start()
