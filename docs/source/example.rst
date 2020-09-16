Example: Wrapping a C model
===========================

In this example, we'll use the *babelizer*
to wrap the *heat* model from the `bmi-example-c`_ repository,
allowing it to be run in Python.
The model and its BMI are written in C.
To simplify package management in the example,
we'll use :term:`conda`.
We'll also use :term:`git` to obtain the model source code.

This is a somewhat long example.
To break it up,
here are the steps we'll take:

#. Create a :term:`conda environment` that includes software to compile the
   model and wrap it with the *babelizer*
#. Clone the `bmi-example-c`_ repository from GitHub and build the
   *heat* model from source
#. Create a *babelizer* input file for the *heat* model
#. Run the *babelizer* to wrap the model in Python
#. Run the *heat* model in Python through *pymt*

Before we begin,
create a directory to hold the work we'll do:

.. code:: bash

  $ mkdir build
  $ cd build


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

Download :download:`this file <environment.yml>`
and create the new environment with:

.. code:: bash

  $ conda env create --file=environment.yml

When this command completes,
activate the *wrap* environment:

.. code:: bash

  $ conda activate wrap

The *wrap* environment now contains all the dependencies needed
to build, install, and wrap the *heat* model.


Build the *heat* model from source
----------------------------------

Clone the `bmi-example-c`_ repository from GitHub:

.. code:: bash

  $ git clone https://github.com/csdms/bmi-example-c

The repository `README`_ contains general instructions for building and installing
this package on Linux, macOS, and Windows.
We'll augment those instructions
with the note that we're installing into the *wrap* conda environment,
so the ``CONDA_PREFIX`` environment variable
should be used to specify the install path.

Linux and macOS
...............

On Linux and macOS,
use these commands to build and install the *heat* model:

.. code:: bash

  $ cd bmi-example-c
  $ mkdir _build && cd _build
  $ cmake .. -DCMAKE_INSTALL_PREFIX=$CONDA_PREFIX
  $ make
  $ make install

Verify the install by testing for the existence of the header
of the library containing the compiled *heat* model:

.. code:: bash

  $ test -f $CONDA_PREFIX/include/bmi_heat.h

Windows
.......

Building on Windows requires
Microsoft Visual Studio 2017 or Microsoft Build Tools for Visual Studio 2017.
To build and install the *heat* model,
the following commands must be run in a `Developer Command Prompt`_:

.. code::

  > cd bmi-example-c
  > mkdir _build && cd _build
  > cmake .. ^
      -G "NMake Makefiles" ^
      -DCMAKE_INSTALL_PREFIX=%CONDA_PREFIX% ^
      -DCMAKE_BUILD_TYPE=Release
  > cmake --build . --target install --config Release

Verify the install by testing for the existence of the header
of the library containing the compiled *heat* model:

.. code::

  > if not exist %LIBRARY_INC%\\bmi_heat.h exit 1 

Create the *babelizer* input file
---------------------------------

The *babelizer* input file provides information to the *babelizer*
about the model to be wrapped.
The input file is created with the ``babelize generate`` subcommand.

Return to our initial ``build`` directory and call ``babelize generate`` with:

.. code:: bash

  $ cd ~/build
  $ babelize generate babel_heatc.toml \
      --language=c \
      --summary="PyMT plugin for heat model" \
      --entry-point=HeatModel=bmiheatc:register_bmi_heat \
      --name=heatc \
      --requirement=""

In this call,
the *babelizer* will also interactively prompt for author name, author email,
GitHub username, and license.
These can be optionally be filled in, or the defaults can be used.

The resulting file, ``babel_heatc.toml``,
will look something like this:

.. include:: babel_heatc.toml
   :literal:

For more information on the entries and sections of the *babelizer* input file,
see `Input file <./readme.html#input-file>`_.


Wrap the model with the *babelizer*
-----------------------------------

Generate Python bindings for the model with the ``babelize init`` subcommand:

.. code:: bash

  $ babelize init babel_heatc.toml .

The results are placed in a new directory, ``pymt_heatc``,
under the current directory.

.. code:: bash

  $ ls -aF pymt_heatc
  ./                        MANIFEST.in               recipe/
  ../                       Makefile                  requirements-library.txt
  .git/                     README.rst                requirements-testing.txt
  .gitignore                babel.toml                requirements.txt
  .travis.yml               docs/                     setup.cfg
  CHANGES.rst               meta/                     setup.py
  CREDITS.rst               pymt_heatc/
  LICENSE                   pyproject.toml

Before we can build the Python bindings,
we must ensure that dependencies required by the toolchain,
as well as any required by the model,
as specified in the *babelizer* input file (none in this case),
are satisfied.

Change to the ``pymt_heatc`` directory and install dependencies
into the conda environment:

.. code:: bash

  $ cd pymt_heatc
  $ conda install -c conda-forge --file=requirements.txt --file=requirements-library.txt


Build the Python bindings with:

.. code:: bash

  $ make install

This command sets off a long list of messages,
at the end of which you'll hopefully see:

.. code:: bash

  Successfully installed pymt-heatc

Take a moment to pause and see what we've done.
Start a Python session and try the following commands:

.. code:: python

  >>> from pymt_heatc import HeatModel
  >>> m = HeatModel()
  >>> print(m.get_component_name())
  The 2D Heat Equation

We've imported the *heat* model,
written in C,
into Python!

There are still a few steps remaining...

..
   Links

.. _bmi-example-c: https://github.com/csdms/bmi-example-c
.. _README: https://github.com/csdms/bmi-example-c/blob/master/README.md
.. _Developer Command Prompt: https://docs.microsoft.com/en-us/dotnet/framework/tools/developer-command-prompt-for-vs
