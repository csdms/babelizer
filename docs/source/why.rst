Should I use the *babelizer*?
=============================

To determine if the *babelizer* is right for you,
first be aware of a few requirements.

1. Your model must be written in C, C++, Fortran, or Python
2. Your model must provide a shared library
3. Your model must expose a `Basic Model Interface`_ (BMI) through this library

The most difficult of the three requirements is the last--implementing a BMI.
This involves adding a series of functions with prescribed names,
arguments, and return values for querying and controlling your model.

We have created several resources to help you understand the BMI and to guide you
through the implementation process.

* The `Basic Model Interface`_ documentation provides an overview of the BMI as well
  as a detailed description of all of the BMI functions.
* The following provide a BMI specification for each of the supported languages:

  * `C specification <https://github.com/csdms/bmi-c/>`_
  * `C++ specification <https://github.com/csdms/bmi-cxx/>`_
  * `Fortran specification <https://github.com/csdms/bmi-fortran/>`_
  * `Python specification <https://github.com/csdms/bmi-python/>`_

* The following give examples of a BMI implementation for each of the supported languages:

  * `C example <https://github.com/csdms/bmi-example-c/>`_
  * `C++ example <https://github.com/csdms/bmi-example-cxx/>`_
  * `Fortran example <https://github.com/csdms/bmi-example-fortran/>`_
  * `Python example <https://github.com/csdms/bmi-example-python/>`_

There are lots of other good reasons to create a BMI for
your model--not just so you can bring it into Python with the *babelizer*!
Read all about them in the `Basic Model Interface`_ documentation.

.. Links:

.. _Basic Model Interface: https://bmi.readthedocs.io/
