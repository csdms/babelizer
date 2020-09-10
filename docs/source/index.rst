.. image:: _static/babelizer-logo-lowercase.png
    :align: center
    :scale: 85%
    :alt: babelizer
    :target: https://bmi.readthedocs.io/

.. title:: babelizer


The *babelizer* is an open source Python utility,
developed by the `Community Surface Dynamics Modeling System`_ (CSDMS),
for wrapping models that expose a `Basic Model Interface`_ (BMI)
so they can imported as Python packages.

Supported languages include:

* C
* C++
* Fortran

Within Python, these models, regardless of their core language,
appear as classes that expose a BMI.
Users are then able to run models interactively
through the Python command line or Jupyter Notebook,
and programmatically through Python scripts;
they can also use Python-based BMI tools such as
the `bmi-tester`_, `pymt`_, and `Landlab`_.

	 
User Guide
==========

.. toctree::
   :maxdepth: 1

   installation
   commands
   input_file
   example
   glossary


Help
====

Adding a BMI to a model can be a daunting task.
If you'd like assistance, CSDMS can help.
Depending on your need, we can provide advice or consulting services.
Feel free to contact us through the `CSDMS Help Desk`_.


..
   Links

.. _Community Surface Dynamics Modeling System: https://csdms.colorado.edu
.. _Basic Model Interface: https://github.com/csdms/bmi
.. _bmi-tester: https://github.com/csdms/bmi-tester
.. _pymt: https://pymt.readthedocs.io/
.. _Landlab: https://landlab.github.io/
.. _CSDMS Help Desk: https://github.com/csdms/help-desk
