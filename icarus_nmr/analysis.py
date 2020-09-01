"""
Icarus High Pressure Jump log files analysis software
author: Valentyn Stadnytskyi
Date: June 2019- July 2019

How it supposed to work.

The class Dataset points at a logging directory.
The directory will have 1 folder:
- buffer_files
    - time_stamp_period_type-of-trace.csv (example: 1564501923.8782883_0_depre.csv
        -> where time = 1564501923.8782883, period = 0 and type-of-data = depre (depressure event))
and 3 files
- experiment.log
- experiment.pickle - a pickled version of processed experiment.log file.
- experiment_parameters.log - a dump of all variable from all modules mostly for debugging purposes.
"""

from numpy import gradient, transpose, genfromtxt, nanmean, argwhere, where, nan, isnan, asarray
import os
import pickle
from logging import debug, info, warn, error

class Dataset():
    def __init__(self, folder = None):
        """

        :param folder: folder, defaults to None
        :type folder: str
        :param log_header: log_header, defaults to None
        :type log_header: list

        """
        ### Log folder related
        self.folder = folder #the pointer at the log folder
        ###Log file related
        self.log_header = None #the header retrieved from experiment.log
        self.log_data = None
        self.log_raw_data = None
        self.log_length = 0
        self.description = ''
        #Traces
        #a dictionary of length for each trace type.
        self.trace_length = {'pre':None, 'depre':None, 'period': None, 'pump':None, 'meanbit3': None, 'cooling': None}
        #a dictionary of lists of different trace types.
        self.trace_lists = {'pre':None, 'depre':None, 'period': None, 'pump':None, 'meanbit3': None, 'cooling': None}
        #auxiliary variables
        self.i = 0
        if folder is not None:
            self.init()

    def init(self):
        from time import time
        import os
        t1 = time()
        self.is_init_done = False
        if self.folder is not None:
            #check if the folder path ends with '/' and add if it is not.
            if self.folder[-1] != '/':
                self.folder += '/'
            #get the list of all trace types and put in appropriate dictionary entry
            for key in self.trace_lists.keys():
                self.trace_lists[key] = self.get_lst(self.folder, key)
                self.trace_length[key] = len(self.trace_lists[key])
            #get log_header
            self.log_header = self.log_read_header(self.folder)
            #check if pickle file exist and load it
            self.log_rawdata,self.log_data = self.log_read_file(self.folder)

            self.log_length = self.log_data.shape[0]
            self.is_init_done = True
        else:
            self.is_init_done  = False

        t2 = time()
        dt = t2-t1
        print('Init of Dataset from folder = {} has status {}. It took {} seconds.'.format(self.folder,self.is_init_done,dt))

    # def dump_to_pickle_file(self, data = None):
    #     """
    #     pickles data and puts it on the drive. the default name is experiment.pickle (similar to original experiment.log)
    #
    #
    #     Parameters
    #     ----------
    #     data: numpy array
    #         data to append
    #
    #     Returns
    #     -------
    #
    #     Examples
    #     --------
    #     >>> dataset = Dataset()
    #     >>> dataset.dump_to_pickle_file(data = data)
    #
    #     """
    #     from pickle import dump, HIGHEST_PROTOCOL
    #     if data is not None:
    #         with open(self.folder + 'experiment.pickle', 'wb') as file:
    #             dump(obj = data, file = file, protocol=HIGHEST_PROTOCOL)

    def log_read_header(self, folder):
        """
        looks for experiment.log file in the specified folder. Reads it and returns header. The typical folder name is /YEAR-MM-DD-hh-mm-ss, where MM - month, DD - day, hh - hours(24 hours), mm-minutes, ss-seconds

        Parameters
        ----------
        folder: string
            folder name

        Returns
        -------
        data: numpy array
            data to append

        Examples
        --------
        >>> dataset = Dataset()
        >>> folder = '/2019-05-31-13-13-52/'
        >>> header = dataset.log_read_header(folder = folder)
        >>> header

        """
        header = ""
        with open(folder + 'experiment.log', "r") as f:
            a = f.readline()
            a = f.readline()
        header = a.replace("b'","").replace("'","").replace("\n","").replace(" ","").split(',')

        return header

    def log_read_file(self, folder):
        """
        converts raw log file data to collapsed 2D numpy array where every entry corresponds to one period. The time stamp on the period will be taken from the period event, which is defined elsewhere.

        looks for experiment.log file in the specified folder. Reads it and returns data as numpy array. The typical folder name is /YEAR-MM-DD-hh-mm-ss, where MM - month, DD - day, hh - hours(24 hours), mm-minutes, ss-seconds

        Parameters
        ----------
        folder: string
            folder name

        Returns
        -------
        data: numpy array
            data to append

        Examples
        --------
        >>> folder = '/2019-05-31-13-13-52/'
        >>> raw_data, data = dataset.log_read_file(folder = folder)
        >>> raw_data.shape
        (980, 37)
        >>> data.shape
        (403, 37)

        """
        from os.path import exists
        raw_data = genfromtxt(folder + 'experiment.log', delimiter = ',', skip_header = 2)
        if exists(folder + 'experiment.pickle'):
            print('the experiment.pickle file in the folder {} was detected and will be uploaded'.format(folder))
            # read processed data from .pickle file
            data = self.log_load_pickle_file(folder)

        else:
            info('the pickle file in the folder {} was NOT detected and the processing of the raw .log file is initiated'.format(folder))
            data =  self.combine_log_entries(raw_data)
            self.dump_to_pickle_file(data)

        return raw_data, data

    def log_load_pickle_file(self, folder):
        """
        checks if the pickle file exist and loads it

        Parameters
        ----------
        folder: string
            folder name

        Returns
        -------
        data: numpy array
            data to append
        rawdata: numpy array
            data to append

        Examples
        --------
        >>> folder = '/2019-05-31-13-13-52/'
        >>> data = dataset.log_read_raw_data(folder = folder)
        >>> data.shape

        """
        from pickle import load
        with open(self.folder + 'experiment.pickle', 'rb') as file:
            data = load(file)
        return data

    def dump_to_pickle_file(self, obj = None):
        """
        pickles data and puts it on the drive. the default name is experiment.pickle (similar to original experiment.log)


        Parameters
        ----------
        data: numpy array
            data to append

        Returns
        -------

        Examples
        --------
        >>> dataset = Dataset()
        >>> dataset.dump_to_pickle_file(data = data)

        """
        from pickle import dump, HIGHEST_PROTOCOL
        if obj is not None:
            with open(self.folder + 'experiment.pickle', 'wb') as file:
                dump(obj = obj, file = file, protocol=HIGHEST_PROTOCOL)

    def get_lst(self,folder = '', type = 'cooling'):
        from numpy import genfromtxt
        import os
        dir_lst = os.listdir(folder + "buffer_files/")
        temp_lst = []
        for item in dir_lst:
            if '_'+type in item and '._' not in item:
                t_lst = item.split('_')
                t_lst.append(item)
                temp_lst.append(t_lst)
        lst2 = sorted(temp_lst, key=lambda x: int(x[1]))
        return lst2

    def combine_log_entries(self,raw_data):
        """
        combines all entries associated with one period in one entry.       converts raw log file data to collapsed 2D numpy array where every entry corresponds to one period. The time stamp on the period will be taken from the period event, which is defined elsewhere.

        Parameters
        ----------
        raw_data: numpy array
            raw data from original log file

        Returns
        -------
        data: numpy array
            compressed data

        Examples
        --------
        >>> folder = '/2019-05-31-13-13-52/'
        >>> raw_data = genfromtxt(folder + 'experiment.log', delimiter = ',', skip_header = 2)
        >>> data = dataset.combine_log_entries(raw_data)
        >>> data.shape

        """
        #find the max period
        max_period = int(max(raw_data[:,2]))
        data = []
        #step thpought every period index and every entry in the header
        for i in list(range(max_period+1)):
            self.i = i
            temp = []
            for j in range(len(self.log_header)):
                #col = 2 is period index
                value = raw_data[where(raw_data[:,2] == i),:][:,:,j][~isnan(raw_data[where(raw_data[:,2] == i),:][:,:,j])]
                if len(value) == 1:
                    temp.append(float(raw_data[where(raw_data[:,2] == i),:][:,:,j][~isnan(raw_data[where(raw_data[:,2] == i),:][:,:,j])]))
                elif len(value) == 0:
                    temp.append(nan)
                elif len(value) >1:
                    temp.append(float(raw_data[where(raw_data[:,2] == i),:][:,:,j][~isnan(raw_data[where(raw_data[:,2] == i),:][:,:,j])][0]))
            data.append(temp)
        return asarray(data)

    def get_log_vector(self,param = 'None'):
        """

        """
        from numpy import squeeze
        try:
            idx = self.log_header.index(param)
        except:
            print(f"param {param} doesn't exist")
            idx = None
        if not None:
            vector = self.period[:,idx]
        return vector

    def get_trace(self,period = 0, type = ''):
        """
        returns the trace numpy array from /buffer_files/

        Parameters
        ----------
        period: integer
            period index number
        type: string
            type of buffer file (pre,depre,pump,cooling, etc)

        Returns
        -------
        data: numpy array
            data to append

        Examples
        --------
        >>> data = dataset.get_trace(period = 2, type = 'pump')
        >>> data.shape
        """
        import os
        from numpy import genfromtxt, transpose
        filename = 'some_nonexisting_file.x'
        for item in self.trace_lists[type]:
            if item[1] == str(period):
                filename = item[3]
        filepath = self.folder + 'buffer_files/'+filename
        exists = os.path.isfile(filepath)
        if exists:
            data = transpose(genfromtxt(filepath,delimiter = ','))
        else:
            data = None
        return data


    def plot_trace(self,type = None, period = None, show = False):
        """
        returns matplotlib figure object of a trace of selected type and period. Returns None if tracefile doesn't exist.

        Parameters
        ----------
        type: string
            type of buffer file (pre,depre,pump,cooling, etc)
        period: integer
            period index number
        show: boolean
            optional plot show flag


        Returns
        -------
        object: matplotlib object
            matplotlib object

        Examples
        --------
        >>> data = dataset.get_trace(period = 2, type = 'pump')
        >>> data.shape
        """
        from matplotlib import pyplot as plt

        # fetch the data from the /buffers/ folder.
        if period is not None and type is not None:
            data = self.get_trace(type = type, period = period)
            if data is not None:
                pass
            else:
                pass
        else:
            return None

    def plot_log(self, type = None):
        """
        returns matplotlib figure object of a trace of selected type and period. Returns None if tracefile doesn't exist.

        Parameters
        ----------
        type: string
            type of buffer file (pre,depre,pump,cooling, etc)
        period: integer
            period index number
        show: boolean
            optional plot show flag


        Returns
        -------
        object: matplotlib object
            matplotlib object

        Examples
        --------
        >>> data = dataset.plot_log(type = 'all')
        >>> data.shape
        """
        pass



if __name__ == '__main__':
    from pdb import pm
    import os
    folder = get_test_folder()
    dataset = Dataset(folder)
