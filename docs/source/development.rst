============
Development
============

If you are interested in assisting with the development of the library or want to have the most recent version of the software to be available for you. You can create a local Git repository on your local machine.

Please visit https://docs.github.com/en/github for more details. Below, you can find a brief instruction how to proceed.

Create GitHub Account
-----------------------------------

the first step is to create a GitHub account if you do not have one. Go here to `Join GitHub for free <https://github.com/join>`_

After create the GitHub account you can familiarize yourself with the system, read many articles online or watch youtube videos.

Fork and Clone GitHub Repository
-----------------------------------

Second, you need to `fork <https://docs.github.com/en/get-started/quickstart/fork-a-repo>`_ the repository and later `clone <https://docs.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository-from-github/cloning-a-repository>`_ it to your local drive.

Installing local repository
-----------------------------------

Now, after cloning the repository, we can install it with PIP. Change directory to the folder with the repository and run.

.. code-block:: python

  pip3 install -e .

This install the local repository as a library in Python. Next, start python, import library and check version.

.. code-block:: python

  python3
  import icarus_nmr #or import icarus_nmr as inmr
  icarus_nmr.__version__ #inmr.__version__

  >> '0.1.0.post2.dev0+g5214016'
