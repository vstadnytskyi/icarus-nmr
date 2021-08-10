=============
Overview
=============
The icarus NMR pressure jump control software is designed to be minimally invasive and provide real-time constant monitoring. The monitoring is done with a fast data acquisition unit from DATAQ DI-4108, which collects data from 8 analog and 7 digital channels.

.. image:: ../files/overview_block_diagram.png
  :width: 600
  :alt: block diagram


The Data Handler process has two main responsibilities:

1. reading data from the DI-4108 built-in buffer and never let the buffer to overflow. The read data is put into FIFO queue of variable length.
2. provide software path to change the digital state on the DI-4108.

The Event Handler process retrieves all new packets of data from the Data Handler's FIFO queue and puts them into a circular buffer. Later new packets from the circular buffer are analyzed for events and results are published via corresponding PVs.

The Graphical User Interface process provides graphical controls and indicators for a user.

The Logging process subscribes to PVs that it is supposed to log.

The DIO Handler (digital input/output handler) aggregates functionality associated with digital input/output on the DI-4108 data acquisition unit.

All communication between these 5 modules is done via Channel Access protocol. 
