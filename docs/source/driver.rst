=============
Driver Level
=============

The library comes with a support for rs232 (slow) and bulk USB(recommended) interfaces. It also has a mock driver that allows testing and debugging of the software.

To import the mock driver instead of actual driver for the DI-4108

.. code-block:: python

  from icarus_nmr.mock_driver import Driver
  driver = Driver()

.. autoclass:: icarus_nmr.mock_driver.Driver
  :members:

Next
