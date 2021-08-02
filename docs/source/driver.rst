=============
Driver Level
=============

The library comes with a support for rs232 (slow) and bulk USB(recommended) interfaces. It also has a mock driver that allows testing and debugging of the software.

To import the  driver for the DI-4108. This library has to be tested manually to insure that all communication with the device is working well. To test the rest of the code, please use the mock driver.

#.. code-block:: python

  #from icarus_nmr.usb_bulk_driver import Driver
  #driver = Driver()

#.. autoclass:: icarus_nmr.usb_bulk_driver.Driver
  #:members:
