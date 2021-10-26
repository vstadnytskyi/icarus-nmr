================
Device Level
================

*****************
Overview
*****************
.. image:: ../files/device_level_diagram.png
  :width: 600
  :alt: device level block diagram

The device level code consists of three major modules(green shaded blocks)

- data acquisition device level module (terminal based)

- Channel Access server modules

- Graphical user interface (PyEpics based)

and two auxiliary modules(blue shaded blocks). The red shaded block is the must dependency without which the device level will simply not run. The driver module can be either real module that connected to a real device or a mock driver that simulates the performance of a real device, see driver section for details. The System Level red shaded block is only one client allowed to connect under normal operating conditions.

*Data acquisition device level*

Data acquisition device level module interacts with the DATAQ-4108 via Python based driver. The module is responsible to retrieve data from the DI-4108 buffer and put it in its' own buffer. The data acquisition module passes digital inputs to the DI-4108. The data acquisition module uses two structures (TODO) and (TODO) to interact with the Channel Access server. The data acquisition server publishes new values (PVs or Process Variables) to a special dictionary that is available to Channel Access module. The acquisition server checks special process variable input dictionary to see if there are any commands that need to be processed.

Data Acquisition Loop

.. image:: ../files/data-acquisition-loop.png
  :width: 600
  :alt: data acquisition loop



*Channel Access server*

The CA server is based on `CAProto library  <https://caproto.github.io/caproto/v0.8.1/>`_ which allows to create channel access servers. The server interacts with device level via two specialized input\output queues (dictionary like). The server checks on a timer if there is anything to do in the input queue and publishes any updates to the output queue if data need to be send to the device level data acquisition module.

*Graphical User interface*

`PyEpics <http://pyepics.github.io/pyepics/>`_ based graphical user interface.



*****************
Device Level
*****************



Start by importing analysis submodule for Icarus Pressure Jump for NMR .

.. code-block:: python

  from icarus_nmr.device_daq import Device
  device = Device()

To import the mock driver instead of actual driver for the DI-4108

.. code-block:: python

  from icarus_nmr.driver_mock import Driver
  driver = Driver()

Next step is to bind the device instance with appropriate driver.

.. code-block:: python

  device.bind_driver(driver)
  device.init()

After the driver is bound, the device instance will use it for all communication with the device (or with the emulator).

.. code-block:: python

  device.bind_driver(driver)
  device.init()

You can peek into the device queue with functions inside of the Queue object.

.. code-block:: python

  data = device.queue.peek_all()

  from matplotlib import pyplot as plt
  plt.figure()
  plt.plot(data[:,5]) #will show sample pressure readings.

*********************
Device Level Client
*********************

There is no client associated with the device level process.

**********************
Device Level Server
**********************

The process variables(PVs) associated with the device level server are:

two main PVs:

* data - next packet of data in the queue (read Only)
* dio - digital input (Write Only)
* queue_length
* packet_shape

auxiliary PVs:

* response - packet size
* serial_number - driver/device serial number
* frequency - data collection frequency
* firmware - firmware
* pressure_sensor_offset - eight integer long array of numbers that offset the sensors

**********************
Device Level Script
**********************



.. autoclass:: icarus_nmr.device_daq.Device
  :members:
