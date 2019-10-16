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

The data in the folder can be visualized. There are several build in functions that can be used to visualize data quickly.

.. code-block:: python

  dataset.plot_history(type = 'all')
  dataset.plot_trace(type = 'pre', index = 1)

The Dataset Class
-------------------------

.. autoclass:: icarus_nmr.analysis.Dataset
  :members:
