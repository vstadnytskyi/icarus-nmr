=============
System Level
=============

Start by importing analysis submodule for Icarus Pressure Jump for NMR .

.. code-block:: python

  from icarus_nmr.system_level import Icarus_SL
  icarus_SL = Icarus_SL()


Digital IO
==========
The DI 4108 has 7 digital input/outputs. Internally the digital state is described as an integer from 0 to 127.

bits
0 : pump
1 : depressurize
2 : pressurize
3 : spare / wired
4 : logging
5 : spare / not wired
6 : spare / not wired

******************************
Definitions of Digital Events
******************************

Pump on/off (bit 0)
=========================
The bit 0 is used to control the high pressure pump air supply valve.

Depressurization event (bit 1)
=================================
The depressurization event is a digital event and is defined as bit 1 going low.

Pressurization event (bit 2)
=============================
The pressurization event is a digital event and is defined as bit 2 going low.

Auxiliary event (bit 3)
=======================
Bit 3 can be used to measure origin pressure. The mean pressure while bit 3 is low will be reported when the bit 3 goes back high.

Logging event  (bit 4)
=======================
The logging starts when the bit 4 goes low and end when bit 4 goes high.

Spare bits (bit 5 and 6)
==========================
There are two spare bits that are not wired but can be used to mark events during data collection.

******************************
Definitions of Analog Events
******************************

The analog events are ....

Pump Stroke event (analog)
============================
The pump stroke event is an analog event. It is defined as ...

Full period event (analog)
============================


Full timeout period event (analog)
===================================
The timeout period is defined as
