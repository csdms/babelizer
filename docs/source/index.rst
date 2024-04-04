.. image:: _static/babelizer-logo-lowercase.png
    :align: center
    :scale: 85%
    :alt: babelizer
    :target: https://babelizer.readthedocs.io/

.. title:: babelizer


The *babelizer* is an open source Python utility,
developed by the `Community Surface Dynamics Modeling System`_ (CSDMS),
for wrapping models that expose a `Basic Model Interface`_ (BMI)
so they can be imported as Python packages.

Supported languages include:

* C
* C++
* Fortran
* Python

Within Python, these models, regardless of their core language,
appear as classes that expose a BMI.
Users are then able to run models interactively
through the Python command line or Jupyter Notebook,
and programmatically through Python scripts;
they can also use Python-based BMI tools such as
the `bmi-tester`_, `pymt`_, and `Landlab`_.

The *babelizer* is an element of the `CSDMS Workbench`_,
an integrated system of software tools, technologies, and standards
for building and coupling models.


User Guide
==========

.. toctree::
   :maxdepth: 2

   readme
   cli
   example-c
   example-fortran
   glossary


API Reference
=============

If you are looking for information on a specific function, class, or
method, this part of the documentation is for you.

.. toctree::
   :maxdepth: 2

   api/index


Additional Information
======================

.. toctree::
   :maxdepth: 2

   authors
   changelog
   contributing
   code-of-conduct
   license

Help
----

Adding a BMI to a model and babelizing it can be a daunting task.
If you'd like assistance, CSDMS can help.
Depending on your need, we can provide advice or consulting services.
Feel free to contact us through the `CSDMS Help Desk`_.

Acknowledgments
---------------

This work is supported by the National Science Foundation
under Award No. `1831623 <https://nsf.gov/awardsearch/showAward?AWD_ID=1831623>`_,
*Community Facility Support: The Community Surface Dynamics Modeling System (CSDMS)*.

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


..
   Links

.. _Community Surface Dynamics Modeling System: https://csdms.colorado.edu
.. _Basic Model Interface: https://github.com/csdms/bmi
.. _bmi-tester: https://github.com/csdms/bmi-tester
.. _pymt: https://pymt.readthedocs.io/
.. _Landlab: https://landlab.github.io/
.. _CSDMS Workbench: https://csdms.colorado.edu/wiki/Workbench
.. _CSDMS Help Desk: https://github.com/csdms/help-desk
