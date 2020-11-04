.. image:: https://travis-ci.com/csdms/babelizer.svg?branch=develop
        :target: https://travis-ci.com/csdms/babelizer

.. image:: https://readthedocs.org/projects/babelizer/badge/?version=latest
        :target: https://babelizer.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
        :target: https://github.com/csdms/babelizer

=============
The Babelizer
=============

Wrap BMI libraries with Python bindings


*****
About
*****

The *babelizer* is a utility for wrapping libraries, from a variety of
languages, that expose a Basic Model Interface (BMI) so that they can be
imported as a Python package.


Supported languages:

*  C
*  C++
*  Fortran

************
Requirements
************

The *babelizer* requires Python >=3.8.


Apart from Python, the *babelzer* has a number of other requirements, all of which
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

To install the *babelizer*, first create a new environment in
which *babelizer* will be installed. This, although not necessary, will
isolate the installation so that there won't be conflicts with your
base *Python* installation. This can be done with *conda* as,

.. code:: bash

    $ conda create -n babelizer python=3
    $ conda activate babelizer

Stable Release
==============

The *babelizer*, and its dependencies, is best installed with *conda*,

.. code:: bash

    $ conda install babelizer -c conda-forge

From Source
===========

After downloading the the *babelizer* source code, run the following from
*babelizer*'s top-level folder (the one that contains *setup.py*) to
install *babelizer* into the current environment::

  $ pip install -e .


**********
Input file
**********

The *babelizer* requires a single, *toml*-formatted, input file that describes
the library you would like to wrap. This file is typically named *babel.toml*.
An example of a blank *babel.toml* file,

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
    package_author = "csdms"
    package_author_email = "csdms@colorado.edu"
    package_license = "MIT"
    summary = ""

You can generate *babel.toml* files using the *babelize generate* command.
For example, the above *babel.toml* was generated with,

.. code:: bash

  $ babelize generate --no-input -

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

Descriptive infomation about the package.

Github username
---------------

The GitHub username or organization where this package will be hosted. This
is used in generating links to the CI, docs, etc.

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
    package_author = "csdms"
    package_author_email = "csdms@colorado.edu"
    package_license = "MIT"
    summary = "PyMT plugin for hydrotrend"

You can use the ``babelize generate`` command to generate *babel.toml* files.
For example the above *babel.toml* can be generated with the following,

.. code:: bash

    $ babelize generate babel.toml \
	  --package=pymt_hydrotrend \
	  --summary="PyMT plugin for hydrotrend" \
	  --language=c \
	  --library=bmi_hydrotrend \
	  --header=bmi_hydrotrend.h \
	  --entry-point=register_bmi_hydrotrend \
	  --name=Hydrotrend \
	  --requirement=hydrotrend

***
Use
***

Generate Python bindings for a library that implements a BMI,
sending output to the current directory

.. code:: bash

  $ babelize init babel.toml .

Update an existing repository

.. code:: bash

  $ babelize update

For a complete example of using the *babelizer*
to wrap a C library exposing a BMI,
see the User Guide of the `documentation`_.


.. _documentation: https://babelizer.readthedocs.io/
