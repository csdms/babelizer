.. image:: https://joss.theoj.org/papers/10.21105/joss.03344/status.svg
    :target: https://doi.org/10.21105/joss.03344

.. image:: https://github.com/csdms/babelizer/workflows/Build/Test%20CI/badge.svg
    :target: https://github.com/csdms/babelizer/actions?query=workflow%3A%22Build%2FTest+CI%22

.. image:: https://anaconda.org/conda-forge/babelizer/badges/version.svg
    :target: https://anaconda.org/conda-forge/babelizer

.. image:: https://readthedocs.org/projects/babelizer/badge/?version=latest
        :target: https://babelizer.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
        :target: https://github.com/csdms/babelizer

.. image:: https://coveralls.io/repos/github/csdms/babelizer/badge.svg?branch=develop
    :target: https://coveralls.io/github/csdms/babelizer?branch=develop


The Babelizer: Wrap BMI libraries with Python bindings
======================================================


The *babelizer* is a utility for wrapping a library that exposes a `Basic Model Interface`_ (BMI) so that it can be
imported as a Python package.

Supported languages include:

*  C
*  C++
*  Fortran
*  Python

Full documentation for the *babelizer*, including examples,
can be found at https://babelizer.readthedocs.io/.


The Babelizer is part of the CSDMS Workbench
--------------------------------------------

The *babelizer* is an element of the `CSDMS Workbench`_,
an integrated system of software tools, technologies, and standards
for building and coupling models. The Workbench provides two Python
frameworks for model coupling, *pymt* and *landlab*.
The *babelizer* was written to bring models written in other languages into
these frameworks.
However, as long as your model
satisfies the requirements below, you can use the *babelizer*
to bring your model into Python without having to use any of the
other tools in the Workbench.

Installation
------------

The quickest way to install the *babelizer* is with *conda*:

.. code:: bash

  conda install -c conda-forge babelizer

For more detailed information,
including how to install the *babelizer* from source,
see the `installation instructions`_ in the documentation.

.. Links:

.. _Basic Model Interface: https://bmi.readthedocs.io/
.. _CSDMS Workbench: https://csdms.colorado.edu/wiki/Workbench
.. _documentation: https://babelizer.readthedocs.io/
.. _BMI C: https://github.com/csdms/bmi-c/
.. _BMI C++: https://github.com/csdms/bmi-cxx/
.. _BMI Fortran: https://github.com/csdms/bmi-fortran/
.. _BMI Python: https://github.com/csdms/bmi-python/
.. _BMI example C: https://github.com/csdms/bmi-example-c/
.. _BMI example C++: https://github.com/csdms/bmi-example-cxx/
.. _BMI example Fortran: https://github.com/csdms/bmi-example-fortran/
.. _BMI example Python: https://github.com/csdms/bmi-example-python/
.. _installation instructions: https://babelizer.readthedocs.io/en/latest/install.html
