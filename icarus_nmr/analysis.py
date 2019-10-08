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

__version__ = '0.0.2'
from matplotlib import pyplot as plt
from numpy import gradient, transpose, genfromtxt, nanmean, argwhere, where, nan, isnan, asarray
import os
import pickle

class Dataset():
    def __init__(self):
        ### Log folder related
        self.folder = None #the pointer at the log folder

        ###Log file related
        self.log_header = None #the header retrieved from experiment.log
        self.log_data = None
        self.log_length = 0
        self.description = ''
        #Traces
        #a dictionary of length for each trace type.
        self.trace_length = {'pre':None, 'depre':None, 'period': None, 'pump':None, 'meanbit3': None, 'cooling': None}
        #a dictionary of lists of different trace types.
        self.trace_lists = {'pre':None, 'depre':None, 'period': None, 'pump':None, 'meanbit3': None, 'cooling': None}

        #auxiliry variables
        self.i = 0

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
            if os.path.exists(self.folder + 'experiment.pickle'):
                print('the experiment.pickle file in the folder {} was detected and will be uploaded'.format(self.folder))
                self.log_data = self.load_pickled_log(self.folder)
            else:
                info('the pickle file in the folder {} was NOT detected and the processing of the raw .log file is initiated'.format(self.folder))
                self.log_data = self.log_read_raw_data(self.folder)
                self.dump_to_picle_file(self.log_data)
            self.log_length = self.log_data.shape[0]
            self.is_init_done = True
        else:
            self.is_init_done  = False

        t2 = time()
        dt = t2-t1
        print('Init of Dataset from folder = {} has status {}. It took {} seconds.'.format(self.folder,self.is_init_done,dt))

    def dump_to_picle_file(data = None):
        from pickle import dump, HIGHEST_PROTOCOL
        if data is not None:
            with open(self.folder + 'experiment.pickle', 'wb') as handle:
                dump(self.log_data, handle, protocol=HIGHEST_PROTOCOL)

    def log_read_header(self, folder):
        with open(folder + 'experiment.log', "r") as f:
            a = f.readline()
            a = f.readline().replace('b','').replace('\n','').replace(' ','').replace("'","")
            header = a.split(',')
        return header

    def log_read_raw_data(self, folder):
        """
        read log folder:
        create
        """
        raw_data = genfromtxt(folder + 'experiment.log', delimiter = ',', skip_header = 2)
        data = self.combine_log_entries(data)
        return data

    def load_pickled_log(self, folder):
        """
        reads pickled file from the folder and
        """
        with open(self.folder + 'experiment.pickle', 'rb') as file:
            log_data = pickle.load(file)
        return log_data

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



    def get_history_log(self):
        history_log= genfromtxt(self.folder + 'experiment.log', delimiter = ',', skip_header = 2)
        dic = {} #create dictionary
        i = 0
        for key in self.log_header:
            if key != "":
                dic[key] = history_log[:,i]
                i+=1
        return dic

    def combine_log_entries(self,data):
        """
        combines all entries associated with one period in one entry.
        """
        max_period = int(max(history_log[:,2]))
        data = []
        for i in list(range(max_period+1)):
            self.i = i
            temp = []
            for j in range(len(self.log_header)):
                value = data[where(raw_data[:,2] == i),:][:,:,j][~isnan(raw_data[where(raw_data[:,2] == i),:][:,:,j])]
                if len(value) == 1:
                    temp.append(float(raw_data[where(raw_data[:,2] == i),:][:,:,j][~isnan(raw_data[where(raw_data[:,2] == i),:][:,:,j])]))
                elif len(value) == 0:
                    temp.append(nan)
                elif len(value) >1:
                    temp.append(float(raw_data[where(raw_data[:,2] == i),:][:,:,j][~isnan(raw_data[where(raw_data[:,2] == i),:][:,:,j])][0]))
            data.append(temp)
        return asarray(data)

    def get_log_vector(self,param = 'None'):
        from numpy import squeeze
        try:
            idx = self.log_header.index(param)
        except:
            print("param %r doesn't exist" %param)
            idx = None
        if not None:
            vector = self.period[:,idx]
        return vector

    def get_trace(self,period = 0, type = ''):
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

if __name__ == '__main__':
    import unittest
    from pdb import pm
    import os
    ##Examples of commands
    ## to get a trace: dataset_1.get_trace(i,'pre') -> return a pressurization trace of all 10 channels at period i
    ## to get a vector from log file for given parameter: dataset_1.get_log_vector(param = 'tSwitchDepressure_1')
    main_folder = '/Volumes/C/Pressure-Jump-NMR/icarus-ii-50/'
    folder = 'test_dataset/'
    dataset = Dataset()
    dataset.folder = folder
    dataset.init()
