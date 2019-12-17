=============
Device Level
=============

Start by importing analysis submodule for Icarus Pressure Jump for NMR .

.. code-block:: python

  from icarus_nmr.device import DI4108_DL

To import the mock driver instead of actual driver for the DI-4108

.. code-block:: python

  from icarus_nmr.mock_driver import Driver
  driver = Driver()

Next step is to bind the device instance with appropriate driver.

.. code-block:: python

  device.bind_driver(driver)

After the driver is bound, the device instance will use it for all communication with the device (or with the emulator).

.. autoclass:: icarus_nmr.device.DI4108_DL
  :members:
