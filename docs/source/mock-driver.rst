===================
Mock Driver Level
===================

The library comes with a support for rs232 (slow) and bulk USB(recommended) interfaces. It also has a mock driver that allows testing and debugging of the software.

To import the mock driver instead of actual driver for the DI-4108

.. code-block:: python

  In [1]: from icarus_nmr.mock_driver import Driver

  In [2]: driver = Driver()

To fully initialize the driver and start the data collection.

.. code-block:: python

  In [3]: driver.init()

  In [4]: driver.get_hardware_information()
  Out[4]:
  {b'Device name': '4108',
  b'Firmware version': 'VS',
  b'Serial Number': '00000000',
  b'Sample Rate Divisor': '60000000'}

The current readings can be requested.

.. code-block:: python

  In [6]: driver.get_readings()
  Out[6]:
  (array([[10999,    -9,  8005,    28,  7979, 10966,  9028,   -13,     0,
             127]], dtype=int16), True)

The mock driver generates random data to simulate actual data stream from DI-4108. These are the control variables that define what is the level of a signal and what is noise.

.. code-block:: python

  In [8]: driver.sim_digital
  Out[8]: 127

  In [9]: driver.sim_analog
  Out[9]: [11000, 0, 8000, 0, 8000, 11000, 9000, 0]

  In [10]: driver.sim_analog_std
  Out[10]: [30, 30, 30, 30, 30, 30, 30, 30]


One can also request a pressurization or depressurization traceback

.. plot:: ./examples_py/get_depre_trace.py
   :include-source:

Detailed description of the function and properties of the mock_driver class below.

.. autoclass:: icarus_nmr.mock_driver.Driver
  :members:
