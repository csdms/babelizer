.. image:: https://github.com/csdms/babelizer/workflows/Build/Test%20CI/badge.svg
    :target: https://github.com/csdms/babelizer/actions?query=workflow%3A%22Build%2FTest+CI%22

.. image:: https://anaconda.org/conda-forge/babelizer/badges/version.svg
    :target: https://anaconda.org/conda-forge/babelizer

.. image:: https://readthedocs.org/projects/babelizer/badge/?version=latest
        :target: https://babelizer.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
        :target: https://github.com/csdms/babelizer

======================================================
The Babelizer: Wrap BMI libraries with Python bindings
======================================================


The *babelizer* is a utility for wrapping a library that exposes a `Basic Model Interface`_ (BMI) so that it can be
imported as a Python package.

Supported languages include:

*  C
*  C++
*  Fortran
*  Python


********************************************
The Babelizer is part of the CSDMS Workbench
********************************************

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


***************************
Should I use the babelizer?
***************************

To determine if the
*babelizer* is right for you, first be aware of a few requirements.

1. Your model must be written in C, C++, Fortran, or Python
2. Your model must provide a shared library
3. Your model must expose a `Basic Model Interface`_ through this library

The most difficult of the three requirements is the last--implementing a BMI. This
involves adding a series of functions with prescribed names,
arguments, and return values for querying and controlling your model. We have created
several resources to help you understand the BMI and to guide you
through the implementation process.

BMI resources
=============

* The `Basic Model Interface`_ documentation provides an overview of the BMI as well
  as a detailed description of all of the BMI functions.
* The following provide a BMI specification for each of the supported languages:

  * `C spec <https://github.com/csdms/bmi-c/>`_
  * `C++ spec <https://github.com/csdms/bmi-cxx/>`_
  * `Fortran spec <https://github.com/csdms/bmi-fortran/>`_
  * `Python spec <https://github.com/csdms/bmi-python/>`_

* The following give examples of a BMI implementation for each of the supported languages:

  * `C example <https://github.com/csdms/bmi-example-c/>`_
  * `C++ example <https://github.com/csdms/bmi-example-cxx/>`_
  * `Fortran example <https://github.com/csdms/bmi-example-fortran/>`_
  * `Python example <https://github.com/csdms/bmi-example-python/>`_

Note
====

There are lots of other good reasons to create a BMI for
your model--not just so you can bring it into Python with the *babelizer*!
Read all about them in the `Basic Model Interface`_ documentation.


************
Requirements
************

The *babelizer* requires Python >=3.8.


Apart from Python, the *babelizer* has a number of other requirements, all of which
can be obtained through either *pip* or *conda*, that will be automatically
installed when you install the *babelizer*.

To see a full listing of the requirements, have a look at the project's
*requirements.txt* file.

If you are a developer of the *babelizer* you will also want to install
additional dependencies for running the *babelizer*'s tests to make sure
that things are working as they should. These dependencies are listed
in *requirements-testing.txt*.

************
Installation
************

To install the *babelizer*, first create a new environment.
Although this isn't strictly necessary, it
isolates the installation to avoid conflicts with your
base Python installation. This can be done with *conda*:

.. code:: bash

    $ conda create -n babelizer python=3
    $ conda activate babelizer

Stable Release
==============

The *babelizer* and its dependencies are best installed with *conda*:

.. code:: bash

    $ conda install babelizer -c conda-forge

From Source
===========

After downloading the the *babelizer* source code, run the following from
*babelizer*'s top-level directory (the one that contains *setup.py*) to
install *babelizer* into the current environment:

  $ pip install -e .


**********
Input file
**********

The *babelizer* requires a single *toml*-formatted input file that describes
the library to wrap. This file is typically named *babel.toml*.
An example of a blank *babel.toml* file:

.. code:: toml

    [library]
    [library."<name>"]
    language = "c"
    library = ""
    header = ""
    entry_point = ""

    [build]
    undef_macros = []
    define_macros = []
    libraries = []
    library_dirs = []
    include_dirs = []
    extra_compile_args = []

    [package]
    name = ""
    requirements = []

    [info]
    github_username = "pymt-lab"
    github_branch = "main"
    package_author = "csdms"
    package_author_email = "csdms@colorado.edu"
    package_license = "MIT"
    summary = ""

    [ci]
    python_version = ["3.9"]
    os = ["linux", "mac", "windows"]

You can generate *babel.toml* files using the *babelize generate* command.
For example, the above *babel.toml* was generated with:

.. code:: bash

  $ babelize generate > babel.toml

Library section
===============

The *library* section specifies information about the library being babelized.

Name
----

The name of the babelized class.
This will be a Python class,
so it should follow Python naming conventions such as camel-case typing.

Language
--------

The programming language of the library (possible values are "c", "c++",
"fortran", and "python").

.. code:: toml

  [library]
  language = "c"

Library
-------

The name of the BMI library to wrap.
This is the text passed to the linker through the `-l` option;
for example, use "foo" for a library *libfoo.a*.

Header
------

The name of the header file (*.h*, *.hxx*) declaring the BMI class.
This option is only needed when wrapping C and C++ libraries.

Entry point
-----------

The name of the BMI entry point into the library.
For object-oriented languages,
this is typically the name of a class that implements the BMI.
For procedural languages,
this is typically a function.

An example of a C++ library (*bmi_child*), exposing a class *BmiChild* (which
implements a BMI) might look like the following:

.. code:: toml

   [library]
   [library.Child]
   language = "c++"
   library = "bmi_child"
   header = "bmi_child.hxx"
   entry_point = "BmiChild"

whereas a C library (*bmi_cem*), exposing a function *register_bmi_cem* (which
implements a BMI) might look like:

.. code:: toml

   [library]
   [library.Cem]
   language = "c"
   library = "bmi_cem"
   header = "bmi_cem.h"
   entry_point = "register_bmi_cem"

Build section
=============

In the build section the user can specify flags to pass to the compiler
when building the extension.

Package section
===============

Name and extra requirements needed to build the babelized library.

Name
----

Name to use for the wrapped package. This is used when creating the new
package *<package_name>*. For example, the following will create
a new package, *pymt_foo*.

.. code:: toml

  [package]
  name = "pymt_foo"

Requirements
------------

List of packages required by the library being wrapped. For example, the
following indicates that the packages *foo* and *bar* are dependencies
for the package.

.. code:: toml

  [package]
  requirements = [ "foo", "bar",]

Info section
============

Descriptive information about the package.

GitHub username
---------------

The GitHub username or organization where this package will be hosted. This
is used in generating links to the CI, docs, etc.

GitHub branch
---------------

The name of the initial branch in the package's repository.
The default is "main".

Author
------

Author of the wrapped package. Note that this is not the author of the
library being wrapped, just the code generated by the *babelizer*.

Email
-----

Contact email to use for the wrapped package.

License
-------

Specify the Open Source license for the wrapped package. Note that this is not the
license for the library being wrapped, just for the code generated by the *babelizer*.

Summary
-------

A short description of the wrapped library.

CI section
==========

Information about how to set up continuous integration.

.. code:: toml

    [ci]
    python_version = ["3.7", "3.8", "3.9"]
    os = ["linux", "mac", "windows"]


Python version
--------------

A list of Python versions to build and test the generated project with.

Operating system
----------------

A list of operating systems to build the generate project on. Supported values are
*linux*, *mac*, and *windows*.

Example babel.toml
==================

Below is an example of a *babel.toml* file that describes a shared library,
written in C. In this example, the library, *bmi_hydrotrend*, exposes the
function *register_bmi_hydrotrend* that implements a BMI for a component
called *hydrotrend*.

.. code:: toml

    [library]
    [library.Hydrotrend]
    language = "c"
    library = "bmi_hydrotrend"
    header = "bmi_hydrotrend.h"
    entry_point = "register_bmi_hydrotrend"

    [build]
    undef_macros = []
    define_macros = []
    libraries = []
    library_dirs = []
    include_dirs = []
    extra_compile_args = []

    [package]
    name = "pymt_hydrotrend"
    requirements = ["hydrotrend"]

    [info]
    github_username = "pymt-lab"
    github_branch = "main"
    package_author = "csdms"
    package_author_email = "csdms@colorado.edu"
    package_license = "MIT"
    summary = "PyMT plugin for hydrotrend"

    [ci]
    python_version = ["3.7", "3.8", "3.9"]
    os = ["linux", "mac", "windows"]

You can use the ``babelize generate`` command to generate *babel.toml* files.
For example the above *babel.toml* can be generated with the following,

.. code:: bash

    $ babelize generate \
	  --package=pymt_hydrotrend \
	  --summary="PyMT plugin for hydrotrend" \
	  --language=c \
	  --library=bmi_hydrotrend \
	  --header=bmi_hydrotrend.h \
	  --entry-point=register_bmi_hydrotrend \
	  --name=Hydrotrend \
	  --requirement=hydrotrend \
    --os-name=linux,mac,windows \
    --python-version=3.7,3.8,3.9 > babel.toml

***
Use
***

Generate Python bindings for a library that implements a BMI,
sending output to the current directory

.. code:: bash

  $ babelize init babel.toml

Update an existing repository

.. code:: bash

  $ babelize update

For a complete example of using the *babelizer*
to wrap a C library exposing a BMI,
see the User Guide of the `documentation`_.


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

