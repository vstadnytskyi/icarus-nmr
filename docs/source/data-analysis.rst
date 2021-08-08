=============
Data Analysis
=============

Start by importing analysis submodule for Icarus Pressure Jump for NMR .

.. code-block:: python

  from icarus_nmr import analysis

Next step is to create an instance of the Dataset class.

.. code-block:: python

  dataset = analysis.Dataset()
  dataset.folder = 'path/to/the/folder/containing/log/data'
  dataset.description = 'you can write your description here.'
  dataset.init()

All data is stored in one array(dataset.log_data) and the header for that array is stored in dataset.log_header

.. code-block:: python

  dataset.log_header #to see the header
  dataset.log_data[:,4] #to access the 4th column in the log data array

The data in the folder can be visualized. There are several build in functions that can be used to visualize data quickly.

.. code-block:: python

  dataset.plot_history(type = 'all')
  dataset.plot_trace(type = 'pre', index = 1)

The log file has 37 columns
* time - Unix time
* global_pointer - global pointer in circular buffer where the event occurred
* period_idx - index for the period
* event_code - the event integer number see XXX for details
* pPre_0 - pressure (TODO)
* pDepre_0 - (TODO)
* pPre_after_0 - (TODO)
* pDiff_0 - (TODO)
* tSwitchDepressure_0 - (TODO)
* tSwitchDepressureEst_0',
* tSwitchPressure_0',
* tSwitchPressureEst_0 - (TODO)
* gradientPressure_0 - (TODO)
* gradientDepressure_0 - (TODO)
* gradientPressureEst_0 - (TODO)
* gradientDepressureEst_0 - (TODO)
* riseTime_0 - (TODO)
* fallTime_0 - (TODO)
* pPre_1 - (TODO)
* pDepre_1 - (TODO)
* pPre_after_1 - (TODO)
* pDiff_1 - (TODO)
* tSwitchDepressure_1 - (TODO)
* tSwitchPressure_1 - (TODO)
* gradientPressure_1 - (TODO)
* gradientDepressure_1 - (TODO)
* fallTime_1 - (TODO)
* riseTime_1 - (TODO)
* period - (TODO)
* delay - (TODO)
* pressure_pulse_width - (TODO)
* depressure_pulse_width - (TODO)
* pump_stroke - number of pump strokes since last reset
* depressure_valve_counter - (TODO)
* pressure_valve_counter - (TODO)
* leak_value - (TODO)
* meanbit3 - mean value while bit 3 is ?high?


The Dataset Class
-------------------------

.. autoclass:: icarus_nmr.analysis.Dataset
  :members:
