=====
Usage
=====

Instrumentation
-------------------

The library consists of five major modules that provide all necessary functionality. Software is written in a modular, hierarchical way and network delocalized way. There are multiple modules that are imported into scripts. Modules are located in the main directory and scripts are located in the /scripts/ subdirectory

The major modules are divided into submodules:

#. device handler

  * device daq (device_daq.py)
  * device server (device_server.py)

#. digital handler

  * digital handler (dio_handler.py)
  * digital server (dio_server.py)
  * digital client (dio_client.py)

#. event handler

  * event handler (event_handler.py)
  * event daq (event_daq.py)
  * event server (event_server.py)
  * event client (event_client.py)

#. logging handler

  * logging handler (logging_handler.py)
  * logging client (logging_client.py)

Auxiliary modules are:

* driver USB (driver_usb_bulk_di_4108.py)
* driver MOCK (driver_mock.py)
* PyEpics (pyepics.py)


Data Analysis
-------------------

The icarus analysis submodule allow easy and seamless access to the logged data from the pressure jump experiment. The instantiation of the Dataset class creates a link to a folder allowing easy access to the log file and traces.

The Dataset class has
log_header = None
log_data = None
log_length = 0
description = ''
trace_length
trace_lists
