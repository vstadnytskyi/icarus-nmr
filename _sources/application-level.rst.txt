==================
Application Level
==================

.. image:: ../files/application-level-gui.png
  :width: 600
  :alt: application level graphical user interface

The main application graphical user interface (GUI) is divided into three main sections (columns).

The left column shows three graphs and table. The graphs are from the previous full cycle: top: pressurization, middle: depressurization and bottom: full period. The table shows the analysis of the full period.

The middle column shows the logged history and consists of four graphs(from top to bottom): (i) Pressure difference between end of pressurization and just before depressurization; (ii) Pressure after the pressurization; (iii) slope of the pressurization blue and depressurization green; (iv) time to switch between when the signal to switch was sent and actual pressure change occurred. blue - pressurization and green - depressurization; with light shade corresponding to approximated values at the sample.

the right column, from top to bottom:

* server selector
* Pressure in kbar for Target and sample
* pulse counter and number of pulses per pump stroke
* three different operation modes: manual, pulsed and console_counter
* the emergency shut down button
* pump on/off button
* two buttons for manual pressurization and depressurization
* message field for faults and warnings


Modern monitors should have more than HD (1920x1080) resolution. Hence, I propose to use HD resolution as a standard to create the icarus application level GUI. The GUI showed in the picture above is divided into 3 sections and the ration is roughly 2\2\1. Given this the columns should be 768\768\384 pixels wide. Vertically we have 1080 pixels. The middle logging graphs should occupy all vertical space (1080 pixels) and left should be divided into 4 sections with ratio of 1/1/1/2 (1 for figures and 2 for the table)





## The structure of elements in the GUI

The majority of the elements in the GUI are pointing at a specific PV in one of the system level processes. This structure allows a simplest possible GUI where all the smarts are buried in the system level applications. wxPython box sizers were extensively used in the development of the GUI. There are several nested levels of box sizers. ...
