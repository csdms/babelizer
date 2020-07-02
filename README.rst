.. image:: https://img.shields.io/travis/csdms/babelizer.svg
        :target: https://travis-ci.org/csdms/babelizer

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
        :target: https://github.com/csdms/babelizer

=============
The Babelizer
=============

Wrap BMI libraries with Python bindings


About
-----

The *babelizer* is a utility for wrapping libraries, from a variety for
languages, that expose a Basic Model Interface (BMI) so that they can
imported as a Python package.


Supported languages:

*  C
*  C++
*  Fortran

Requirements
------------

The *babelizer* is Python 3 only.


Apart from Python, the *babelzer* has a number of other requirements, all of which
can be obtained through either *pip* or *conda*, that will be automatically
installed when you install the *babelizer*.

To see a full listing of the requirements, have a look at the project's
*requirements.txt* file.

If you are a developer of the *babelizer* you will also want to install
additional dependencies for running the *babelizer*'s tests to make sure
that things are working as they should. These dependencies are listed
in *requirements-testing.txt*.

Installation
------------

To install the *babelizer*, first create a new environment in
which *babelizer* will be installed. This, although not necessary, will
isolate the installation so that there won't be conflicts with your
base *Python* installation. This can be done with *conda* as::

  $ conda create -n babelizer python=3
  $ conda activate babelizer

Stable Release
++++++++++++++

The *babelizer*, and its dependencies, can be installed either with *pip*
or *conda*. Using *pip*::

    $ pip install babelizer

Using *conda*::

    $ conda install babelizer -c conda-forge

From Source
+++++++++++

After downloading the the *babelizer* source code, run the following from
*babelizer*'s top-level folder (the one that contains *setup.py*) to
install *babelizer* into the current environment::

  $ pip install -e .


Input file
----------

The *babelizer* requires a single, *yaml* formatted, input file that describes
the library you would like to wrap. This file is typically called, *babel.yaml*.
An example of a black *babel.yaml* file,

.. code:: yaml

  build:
    define_macros: []
    extra_compile_args: []
    include_dirs: []
    libraries: []
    library_dirs: []
    undef_macros: []
  info:
    github_username:
    plugin_author:
    plugin_license:
    summary:
  library:
    entry_point: []
    language:
    register:
  plugin:
    name:
    requirements: []


Below is an example of a *babel.yaml* file that describes a shared library,
written in C. In this example, the library, *bmi_hydrotrend*, exposes the
function *register_bmi_hydrotrend* that implements a BMI for a component
called *hydrotrend*.

.. code:: yaml

  build:
    define_macros: []
    extra_compile_args: []
    include_dirs: []
    libraries: []
    library_dirs: []
    undef_macros: []
  info:
    github_username: mcflugen
    plugin_author: Eric Hutton
    plugin_license: MIT
    summary: PyMT plugin for hydrotrend
  library:
    entry_point:
    - Hydrotrend=bmi_hydrotrend:register_bmi_hydrotrend
    language: c
    register: ''
  plugin:
    name: hydrotrend
    requirements:
    - hydrotrend

Examples
--------

Generate Python bindings for a C library that implements a BMI,

.. code:: bash

  $ babelize init babel.yaml

Update an existing repository

.. code:: bash

  $ babelize update
