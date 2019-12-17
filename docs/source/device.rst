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

Next step is to initialize the device instance with appropriate driver

.. code-block:: python

  device.init(driver = driver)
  

.. automodule:: icarus_nmr.device
  :members:

  TODO: this is not working yet
