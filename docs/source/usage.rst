=====
Usage
=====

Start by importing Icarus Pressure Jump for NMR.

.. code-block:: python

  import icarus_nmr

Data Analysis
-------------------

The icarus analysis submodule allow easy and seamless access to the logged data from the pressure jump experiment. The instantiation of the Dataset class creates a link to a folder allowing easy access to the log file and traces.

The Dataset class has
  log_header = None #the header retrieved from experiment.log
self.log_data = None
self.log_length = 0
self.description = ''
#Traces
#a dictionary of length for each trace type.
self.trace_length = {'pre':None, 'depre':None, 'period': None, 'pump':None, 'meanbit3': None, 'cooling': None}
#a dictionary of lists of different trace types.
self.trace_lists = {'pre':None, 'depre':None, 'period': None, 'pump':None, 'meanbit3': None, 'cooling': None}

Instrumentation
-------------------
