==========================
Introduction and Overview
==========================

.. image:: ../files/overview_instrument_schematics.jpg
  :width: 600
  :alt: whole instrument schematics

The icarus NMR pressure-jump instrument is a newly developed instrument at Laboratory of Chemical Physics, NIDDK, NIH. The Figure 1 shows the diagram if the first generation apparatus. The apparatus controlling the hydrostatic pressure consists of a high-pressure reservoir of hydraulic fluid, either mineral oil or mineral spirit, that is connected through a spectrometer-controlled valve and stainless-steel tubing to the NMR sample cell (Figure 1). In the open state of the high-pressure valve, the aqueous protein solution inside the NMR sample cell rapidly equilibrates its pressure with the oil reservoir, which itself is pressurized by a pneumatically driven pump. (more details at www.pnas.org/cgi/doi/10.1073/pnas.1803642115)

The high-pressure and low-pressure hydraulic valves can be open and closed by an electrical TTL signal (Active Low) originating at NMR console. The system is equipment with multiple low pressure sensors and high-pressure hydraulic transducer(shown in the Figure 1). The digital TTL lines together with analog sensor readings are connected to the data acquisition unit for monitoring and emergency control.

The icarus NMR pressure jump control software is designed to be minimally invasive and provide real-time constant monitoring. The monitoring is done with a fast data acquisition unit from DATAQ DI-4108, which collects data from 8 analog and 7 digital channels.

.. image:: ../files/overview_block_diagram.png
  :width: 600
  :alt: block diagram


The data acquisition unit(DAQ) (DI-4108 by DATAQ) collects data from all channels at 4kS/s resulting in a stream of data of 16 bit integers. The stream of data is 80kB per second. The DAQ's build-in buffer has capacity of 16kB, hence we need to read data out of the build-in buffer at least once per 200 ms to prevent buffer overflow. The data controller process is responsible to read data in packets (by default 64-long | every 16 ms | 1.280 kBytes). The acquired data goes into device controller numpy queue with the programmatically controller length. If the queue is full, the oldest values are discarded and new one are added at the rear of the queue. The device controller is equipped with server capabilities and can present information in the queue to outside clients.

The event controller process acts as a client and retrieves packets of data from the device controller queue and appends it to the circular buffer. Each packet of data is searched for preprogrammed events. Later events are analyzed and results are presented to upper level clients, e.g. Graphical User Interface and logging controller.

The Graphical User Interface (GUI) presents data as charts or numbers and provides text fields to change parameters and buttons to control valves.
