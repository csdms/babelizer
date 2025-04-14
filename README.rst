|JOSS paper| |Build Status| |Conda Version| |Documentation Status| |Coverage Status|

The Babelizer: Wrap BMI libraries with Python bindings
======================================================

The *babelizer* is an open source Python utility,
developed by the `Community Surface Dynamics Modeling System`_ (CSDMS),
for wrapping a library that exposes a `Basic Model Interface`_ (BMI)
so that it can be imported as a Python package.

Supported languages include:

*  C
*  C++
*  Fortran
*  Python

The *babelizer* is an element of the `CSDMS Workbench`_,
an integrated system of software tools, technologies, and standards
for building and coupling models.

Full documentation for the *babelizer*, including examples,
can be found at https://babelizer.readthedocs.io/.

Installation
------------

The quickest way to install the *babelizer* is with *conda*:

.. code:: bash

  conda install -c conda-forge babelizer

For more detailed information,
including how to install the *babelizer* from source,
see the `installation instructions`_ in the documentation.

Contributing
------------

If you wish to report bugs or request new features for the *babelizer*,
or if you would like to fix bugs and implement new features,
please see our `contributing`_ guidelines.
Contributions to the *babelizer* are `credited`_.

Acknowledgments
---------------

The Community Surface Dynamics Modeling System is funded
by the U.S. National Science Foundation.

.. Links:

.. |JOSS paper| image:: https://joss.theoj.org/papers/10.21105/joss.03344/status.svg
    :target: https://doi.org/10.21105/joss.03344
    :alt: JOSS paper
.. |Build Status| image:: https://github.com/csdms/babelizer/workflows/Build/Test%20CI/badge.svg
    :target: https://github.com/csdms/babelizer/actions?query=workflow%3A%22Build%2FTest+CI%22
    :alt: Build status
.. |Conda Version| image:: https://anaconda.org/conda-forge/babelizer/badges/version.svg
    :target: https://anaconda.org/conda-forge/babelizer
    :alt: Conda version
.. |Documentation Status| image:: https://readthedocs.org/projects/babelizer/badge/?version=latest
    :target: https://babelizer.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation status
.. |Coverage Status| image:: https://coveralls.io/repos/github/csdms/babelizer/badge.svg?branch=develop
    :target: https://coveralls.io/github/csdms/babelizer?branch=develop
    :alt: Coverage status
.. _Community Surface Dynamics Modeling System: https://csdms.colorado.edu
.. _Basic Model Interface: https://bmi.readthedocs.io/
.. _CSDMS Workbench: https://csdms.colorado.edu/wiki/Workbench
.. _installation instructions: https://babelizer.readthedocs.io/en/latest/install.html
.. _contributing: https://babelizer.readthedocs.io/en/latest/contributing.html
.. _credited: https://babelizer.readthedocs.io/en/latest/credits.html
