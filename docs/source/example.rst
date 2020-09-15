Example: Wrapping a C model
===========================

In this example, we'll use the *babelizer*
to wrap the model *heat* from the `bmi-example-c`_ repository,
allowing it to run in Python.
The model and its BMI are written in C.
To simplify package management in the example,
we'll use :term:`conda`.
We'll also use :term:`git` to obtain the model source code.

Starting from the model source code,
here are the steps we'll take to wrap the model:

#. Create a :term:`conda environment` that includes packages to compile the
   model and wrap it with the *babelizer*
#. Clone the `bmi-example-c`_ repository from GitHub and build the
   *heat* model from source
#. Create a *babelizer* input file for the *heat* model
#. Run the *babelizer* to wrap the model in Python
#. Run the *heat* model in Python through *pymt*


Set up a conda environment
--------------------------

Start by setting up a :term:`conda environment`
where we can build and wrap the model.
We'll need a compiler toolchain to build and install the model,
as well as the *babelizer*.
The necessary packages are listed in the conda environment file
:download:`environment.yml`:

.. include:: environment.yml
   :literal:

Download this file and create the new environment with:

.. code:: bash

  conda env create --file=environment.yml

When this command completes,
activate the *wrap* environment:

.. code:: bash

  conda activate wrap

The *wrap* environment now contains all the dependencies needed
to build, install, and wrap the *heat* model.


Build the *heat* model from source
----------------------------------

Clone the `bmi-example-c`_ repository from GitHub:

.. code:: bash

  git clone https://github.com/csdms/bmi-example-c

The repository `README`_ contains general instructions for building and installing
this package on Linux, macOS, and Windows.
We'll augment those instructions
with the note that we're installing into the *wrap* conda environment,
so the ``CONDA_PREFIX`` environment variable
should be used to specify the install path.

Build on Linux and macOS
........................

On Linux and macOS,
use these commands to build and install the *heat* model:

.. code:: bash

  cd bmi-example-c
  mkdir _build && cd _build
  cmake .. -DCMAKE_INSTALL_PREFIX=$CONDA_PREFIX
  make
  make install

Verify the install by testing for the existence of the header
of the library containing the compiled *heat* model:

.. code:: bash

  test -f $CONDA_PREFIX/include/bmi_heat.h

Build on Windows
................

Building on Windows requires
Microsoft Visual Studio 2017 or Microsoft Build Tools for Visual Studio 2017.
To build and install the *heat* model,
the following commands must be run in a `Developer Command Prompt`_:

.. code::

  cd bmi-example-c
  mkdir _build && cd _build
  cmake .. ^
      -G "NMake Makefiles" ^
      -DCMAKE_INSTALL_PREFIX=%CONDA_PREFIX% ^
      -DCMAKE_BUILD_TYPE=Release
  cmake --build . --target install --config Release

Verify the install by testing for the existence of the header
of the library containing the compiled *heat* model:

.. code::

  if not exist %LIBRARY_INC%\\bmi_heat.h exit 1 

Create the *babelizer* input file
---------------------------------


..
   Links

.. _bmi-example-c: https://github.com/csdms/bmi-example-c
.. _README: https://github.com/csdms/bmi-example-c/blob/master/README.md
.. _Developer Command Prompt: https://docs.microsoft.com/en-us/dotnet/framework/tools/developer-command-prompt-for-vs
