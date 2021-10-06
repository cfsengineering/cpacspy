.. image:: https://img.shields.io/pypi/v/cpacspy.svg
    :target: https://pypi.python.org/pypi/cpacspy
    :alt: pypi version

.. image:: https://github.com/cfsengineering/cpacspy/actions/workflows/python-package-conda.yml/badge.svg?branch=main
    :target: https://github.com/cfsengineering/cpacspy/actions/workflows/python-package-conda.yml
    :alt: Pytest status

.. image:: https://img.shields.io/badge/license-Apache%202-blue.svg
    :target: https://github.com/cfsengineering/cpacspy/blob/main/LICENSE.txt
    :alt: License


.. figure:: /logo/logo_white_bg.png
    :width: 300 px
    :align: center
    :alt: cpacspy logo

cpacspy
=======

cpacspy is a Python package to read, write and analyse `CPACS <https://www.cpacs.de/>`_ AeroPerformanceMaps.


Installation
============

You need to have `TIXI <https://github.com/DLR-SC/tixi>`_ and `TIGL <https://github.com/DLR-SC/tigl>`_ install on your computer to use this package. The easiest way is to use a Conda environment, to create one:

- Install Miniconda: https://docs.conda.io/en/latest/miniconda.html

- Clone this repository and create a Conda environment with the following command:

.. code-block:: bash

   $ git clone https://github.com/cfsengineering/cpacspy.git
   $ cd cpacspy
   $ conda env create -f environment.yml
   $ conda activate cpacspy_env

- When it is done or if you already have TIXI and TIGL install on your computer:

.. code-block:: bash

   $ pip install cpacspy


To build and install locally
============================

.. code-block:: bash

   $ cd cpacspy
   $ python -m build
   $ pip install --user .


How to use this package
=======================

To see how to use this module, check out `/example/cpacspy_use.py <https://github.com/cfsengineering/cpacspy/blob/main/examples/cpacspy_use.py>`_


License
=======

**License:** Apache-2.0
