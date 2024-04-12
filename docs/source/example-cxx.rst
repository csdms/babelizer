Example: Wrapping a C++ model
=============================

In this example, we'll use the *babelizer*
to wrap the *heat* model from the `bmi-example-cxx`_ repository,
allowing it to be run in Python.
The model and its BMI are written in C++.
To simplify package management in the example,
we'll use :term:`conda`.
We'll also use :term:`git` to obtain the model source code.

Here are the steps we'll take to complete this example:

#. Create a :term:`conda environment` that includes software to compile the
   model and wrap it with the *babelizer*
#. Clone the `bmi-example-cxx`_ repository from GitHub and build the
   *heat* model from source
#. Create a *babelizer* configuration file describing the *heat* model
#. Run the *babelizer* to generate a Python package, then build and install the package
#. Show the *heat* model running in Python through *pymt*

Before we begin,
create a directory to hold our work:

.. code:: bash

  mkdir example-cxx && cd example-cxx

This directory is a starting point;
we'll add files and directories to it as we proceed through the example.
The final directory structure of ``example-c`` should look similar to that below.

.. code:: bash

  example-cxx/
  ├── babel_heatcxx.toml
  ├── bmi-example-cxx/
  ├── environment-cxx.yml
  ├── pymt_heatcxx/
  └── test/


Set up a conda environment
--------------------------

Start by setting up a :term:`conda environment` that includes the *babelizer*,
as well as a toolchain to build and install the model.
The necessary packages are listed in the conda environment file
:download:`environment-cxx.yml`:

.. include:: environment-cxx.yml
   :literal:

:download:`Download <environment-cxx.yml>` this file
and place it in the ``example-cxx`` directory you created above.
Create the new environment with:

.. code:: bash

  conda env create --file environment-cxx.yml

When this command completes,
activate the environment
(on Linux and macOS, you may have to use ``source`` instead of ``conda``):

.. code:: bash

  conda activate wrap-cxx

The *wrap-cxx* environment now contains all the dependencies needed
to build, install, and wrap the *heat* model.


Build the *heat* model from source
----------------------------------

From the ``example-cxx`` directory,
clone the `bmi-example-cxx`_ repository from GitHub:

.. code:: bash

  git clone https://github.com/csdms/bmi-example-cxx

There are general `instructions`_ in the repository for building and installing
this package on Linux, macOS, and Windows.
We'll augment those instructions
with the note that we're installing into the *wrap-cxx* conda environment,
so the ``CONDA_PREFIX`` environment variable
should be used to specify the install path.

Linux and macOS
...............

On Linux and macOS,
use these commands to build and install the *heat* model:

.. code:: bash

  cd bmi-example-cxx
  mkdir build && cd build
  cmake .. -DCMAKE_INSTALL_PREFIX=$CONDA_PREFIX
  make install

Verify the install by testing for the existence of the header
of the library containing the compiled *heat* model:

.. code:: bash

  test -f $CONDA_PREFIX/include/bmi_heat.hxx ; echo $?

A return of zero indicates success.

Windows
.......

Building on Windows requires
Microsoft Visual Studio 2019 or Microsoft Build Tools for Visual Studio 2019.
To build and install the *heat* model,
the following commands must be run in a `Developer Command Prompt`_:

.. code:: bat

  cd bmi-example-cxx
  mkdir build && cd build
  cmake .. ^
    -G "NMake Makefiles" ^
    -DCMAKE_INSTALL_PREFIX=%CONDA_PREFIX% ^
    -DCMAKE_BUILD_TYPE=Release
  cmake --build . --target install --config Release

Verify the install by testing for the existence of the header
of the library containing the compiled *heat* model:

.. code:: bat

  if not exist %LIBRARY_INC%\\bmi_heat.hxx exit 1

Create a *babelizer* configuration file
---------------------------------------

A *babelizer* configuration file provides information to the *babelizer*
about the model to be wrapped.

Typically, we would use the ``babelize sample-config`` command
to create a sample configuration file that could then be edited.
However, to simplify this example, we have provided a completed
configuration file for the *heat* model.
:download:`Download <babel_heatcxx.toml>` the file
:download:`babel_heatcxx.toml` and copy it to the ``example-cxx`` directory.

The configuration file looks like this:

.. include:: babel_heatcxx.toml
   :literal:

For more information on the entries and sections of the *babelizer* configuration file,
see `Configuration file <./configuration.html>`_.


Wrap the model with the *babelizer*
-----------------------------------

From the ``example-cxx`` directory,
generate a Python package for the model with the ``babelize init`` command:

.. code:: bash

  babelize init babel_heatcxx.toml

The results are placed in a new directory, ``pymt_heatcxx``,
under the current directory.

Build and install the wrapped model
...................................

Change to the ``pymt_heatcxx`` directory,
then build and install the Python package with *pip*:

.. code:: bash

  cd pymt_heatcxx
  pip install ."[dev]"

The ``pip install`` command sets off a long list of messages,
at the end of which you'll hopefully see:

.. code:: bash

  Successfully installed pymt-heatcxx

Pause a moment to see what we've done.
Change back to the initial ``example-cxx`` directory,
make a new ``test`` directory,
and change to it:

.. code:: bash

  cd ..
  mkdir test && cd test

Start a Python session (e.g., run ``python``) and try the following commands:

.. code:: python

  from pymt_heatcxx import HeatCxx
  m = HeatCxx()
  m.get_component_name()

You should see:

.. code:: bash

  The 2D Heat Equation

We've imported the *heat* model,
written in C++,
into Python!
Exit the Python session (e.g. type ``exit()``).

Test the BMI
............

At this point,
it's a good idea to run the *bmi-tester* (`documentation <bmi-tester>`_)
over the model.
The *bmi-tester* exercises each BMI method exposed through Python,
ensuring it works correctly.
However, before running the *bmi-tester*,
one last piece of information is needed.
Like all models equipped with a BMI,
*heat* uses a :term:`configuration file` to specify initial parameter values.
Create a configuration file for *heat* at the command line with:

.. code:: bash

  echo "1.5, 8.0, 6, 5" > config.txt

or download the file :download:`config.txt <examples/config.txt>`,
making sure to place it in the ``test`` directory.

From the ``test`` directory, run the *bmi-tester*:

.. code:: bash

  bmi-test pymt_heatcxx:HeatCxx --config-file=config.txt --root-dir=. -vvv

This command sets off a long list of messages,
ending with

.. code:: bash

  🎉 All tests passed!

if everything has been built correctly.


Make a *pymt* component
-----------------------

The final step in wrapping the *heat* model
is to add metadata used by the `Python Modeling Tool`_, *pymt*.
CSDMS develops a set of standards,
the `CSDMS Model Metadata`_,
that provides a detailed and formalized description of a model.
The metadata allow *heat* to be run and be :term:`coupled <model coupling>`
with other models that expose a BMI and have been similarly wrapped
with the *babelizer*.

Recall the *babelizer* outputs the wrapped *heat* model
to the directory ``pymt_heatcxx``.
Under this directory,
the *babelizer* created a directory for *heat* model metadata,
``meta/HeatCxx``.
Change back to the ``pymt_heatcxx`` directory
and view the current metadata:

.. code:: bash

  cd ../pymt_heatcxx
  ls meta/HeatCxx/

which gives:

.. code:: bash

  api.yaml

The file ``api.yaml`` is automatically generated by the *babelizer*.
To complete the description of the *heat* model,
other metadata files are needed, including:

* :download:`info.yaml <examples/cxx/info.yaml>`
* :download:`run.yaml <examples/cxx/run.yaml>`
* a :download:`templated model configuration file <examples/cxx/heat.txt>`
* :download:`parameters.yaml <examples/cxx/parameters.yaml>`

`Descriptions`_ of these files and their roles
are given in the CSDMS Model Metadata repository.
Download each of the files using the links in the list above
and place them in the ``pymt_heatcxx/meta/HeatCxx`` directory
alongside ``api.yaml``.
The structure of the ``meta`` directory should look like:

.. code:: bash

  meta/
  └── HeatCxx/
      ├── api.yaml
      ├── heat.txt
      ├── info.yaml
      ├── parameters.yaml
      └── run.yaml

Run the babelized model in *pymt*
...................................

Start a Python session and show that the *heat* model
can be called through *pymt*:

.. code:: python

  from pymt.models import HeatCxx
  m = HeatCxx()
  m.name

You should see:

.. code:: bash

  The 2D Heat Equation

A longer example,
:download:`pymt_heatcxx_ex.py <examples/cxx/pymt_heatcxx_ex.py>`,
is included in the documentation.
For easy viewing, it's reproduced here verbatim:

.. include:: examples/cxx/pymt_heatcxx_ex.py
   :literal:

:download:`Download <examples/cxx/pymt_heatcxx_ex.py>` this Python script,
then run it with:

.. code:: bash

  python pymt_heatcxx_ex.py


Summary
-------

Using the *babelizer*, we wrapped the *heat* model, which is written in C++.
It can now be called as a *pymt* component in Python.

The steps for wrapping a model with the *babelizer* outlined in this example
can also be applied to models written in `C`_ and `Fortran`_.


..
   Links

.. _bmi-example-cxx: https://github.com/csdms/bmi-example-cxx
.. _instructions: https://github.com/csdms/bmi-example-cxx/blob/master/README.md
.. _Developer Command Prompt: https://docs.microsoft.com/en-us/dotnet/framework/tools/developer-command-prompt-for-vs
.. _bmi-tester: https://bmi-tester.readthedocs.io
.. _Python Modeling Tool: https://pymt.readthedocs.io
.. _CSDMS Model Metadata: https://github.com/csdms/model_metadata
.. _Descriptions: https://github.com/csdms/model_metadata/blob/develop/README.rst
.. _C: example-c.html
.. _Fortran: example-fortran.html
