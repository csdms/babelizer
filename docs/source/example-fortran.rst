.. _example-fortran:

Example: Wrapping a Fortran model
=================================

In this example, we'll use the *babelizer*
to wrap the *heat* model from the `bmi-example-fortran`_ repository,
allowing it to be run in Python.
The model and its BMI are written in Fortran.
To simplify package management in the example,
we'll use :term:`conda`.
We'll also use :term:`git` to obtain the model source code.

Here are the steps we'll take to complete this example:

#. Create a :term:`conda environment` that includes software to compile the
   model and wrap it with the *babelizer*
#. Clone the `bmi-example-fortran`_ repository from GitHub and build the
   *heat* model from source
#. Create a *babelizer* input file describing the *heat* model
#. Run the *babelizer* to generate a Python package, then build and install the package
#. Show the *heat* model running in Python through *pymt*

Before we begin,
create a directory to hold our work:

.. code:: bash

  $ mkdir example-f && cd example-f

This directory is a starting point;
we'll add files and directories to it as we proceed through the example.
The final directory structure of ``example-c`` should look similar to that below.

.. code:: bash

  example-f/
  ├── babel_heatf.toml
  ├── bmi-example-fortran/
  ├── environment-fortran.yml
  ├── pymt_heatf/
  └── test/

Set up a conda environment
--------------------------

Start by setting up a :term:`conda environment` that includes the *babelizer*,
as well as a toolchain to build and install the model.
The necessary packages are listed in the conda environment file
:download:`environment-fortran.yml`:

.. include:: environment-fortran.yml
   :literal:

:download:`Download <environment-fortran.yml>` this file
and place it in the ``example-f`` directory you created above.
Create the new environment with:

.. code:: bash

  conda env create --file environment-fortran.yml

When this command completes,
activate the environment
(on Linux and macOS, you may have to use ``source`` instead of ``conda``):

.. code:: bash

  conda activate wrap-f

The *wrap-f* environment now contains all the dependencies needed
to build, install, and wrap the *heat* model.


Build the *heat* model from source
----------------------------------

From the ``example-f`` directory,
clone the `bmi-example-fortran`_ repository from GitHub:

.. code:: bash

  git clone https://github.com/csdms/bmi-example-fortran

There are general `instructions`_ in the repository for building and installing
this package on Linux, macOS, and Windows.
We'll augment those instructions
with the note that we're installing into the *wrap* conda environment,
so the ``CONDA_PREFIX`` environment variable
should be used to specify the install path.

Note that if you build the model with the
`Fortran Package Manager <https://fpm.fortran-lang.org/en/index.html>`_
(*fpm*), you will end up with a static library (`.a` on Unix, `.lib` on
Windows) instead of the dynamic library (`.so` on Unix, `.dll` on
Windows) that the CMake build creates. We are aware of
issues linking to the compiler runtime libraries from this static
library, and for this reason we recommend using the CMake build
routine, as detailed below.

Linux and macOS
...............

On Linux and macOS,
use these commands to build and install the *heat* model:

.. code:: bash

  cd bmi-example-fortran
  mkdir build && cd build
  cmake .. -DCMAKE_INSTALL_PREFIX=$CONDA_PREFIX
  make install

Verify the install by testing for the existence of the module
file of the library containing the compiled *heat* model:

.. code:: bash

  test -f $CONDA_PREFIX/include/bmiheatf.mod ; echo $?

A return of zero indicates success.

Windows
.......

Building the *heat* model on Windows requires either:

* A Unix-like system, such as `Cygwin <https://www.cygwin.com/>`_ or
  `Windows Subsystem for Linux <https://learn.microsoft.com/en-us/windows/wsl/>`_,
  in which case you can follow the above Linux and macOS instructions.
* Microsoft Visual Studio 2017 or later, or Microsoft Build Tools for
  Visual Studio 2017 or later, in which case the following instructions should be followed.

Open a `Developer Command Prompt`_ and run:

.. code:: bat

  cd bmi-example-fortran
  mkdir build && cd build
  cmake .. ^
    -G "NMake Makefiles" ^
    -DCMAKE_INSTALL_PREFIX=%CONDA_PREFIX% ^
    -DCMAKE_BUILD_TYPE=Release
  cmake --build . --target install --config Release

Verify the install by testing for the existence of the module
file of the library containing the compiled *heat* model:

.. code:: bat

  if exist %CONDA_PREFIX%\include\bmiheatf.mod echo File exists

Note that on Windows systems, the conda package we specified
called `fortran-compiler` installs a fairly old version of the Flang
compiler, and there are few options for more modern compilers
available via conda (as opposed to for Unix, where modern versions
of `GFortran are available <https://anaconda.org/conda-forge/gfortran>`_).
This is fine for the example *heat* model, but code bases leveraging
newer features of Fortran may need a more modern compiler. In this
case, it might be necessary to install a Fortran compiler separately
to conda, for example using the binaries provided by
`equation.com <http://www.equation.com/servlet/equation.cmd?fa=fortran>`_.
The `BMI bindings <https://github.com/csdms/bmi-fortran>`_ (installed
here via conda) should be compiled with the same compiler as the model
that uses them, to avoid incompatibility issues, and so if you choose
a different compiler than provided by `fortran-compiler`, you will
likely have to compile the BMI bindings with this compiler as well.

Create a *babelizer* configuration file
---------------------------------------

A *babelizer* configuration file provides information to the *babelizer*
about the model to be wrapped.

Typically, we would use the ``babelize sample-config`` command
to create a sample configuration file, which could then be edited.
However, to simplify this example, we have provided a completed
configuration file for the *heat* model.
:download:`Download <babel_heatf.toml>` the file
:download:`babel_heatf.toml` and copy it to the ``example-f`` directory.

The configuration file looks like this:

.. include:: babel_heatf.toml
   :literal:

For more information on the entries and sections of the *babelizer* configuration file,
see `Configuration file <./configuration.html>`_.


Wrap the model with the *babelizer*
-----------------------------------

From the ``example-f`` directory,
generate a Python package for the model with the ``babelize init`` command:

.. code:: bash

  babelize init babel_heatf.toml

The results are placed in a new directory, ``pymt_heatf``,
under the current directory.

Build and install the wrapped model
...................................

Change to the ``pymt_heatf`` directory,
then build and install the Python package with *pip*:

.. code:: bash

  cd pymt_heatf
  pip install ."[dev]"

The ``pip install`` command sets off a long list of messages,
at the end of which you'll hopefully see:

.. code:: bash

  Successfully installed pymt_heatf

Pause a moment to see what we've done.
Change back to the initial ``example-f`` directory,
make a new ``test`` directory,
and change to it:

.. code:: bash

  cd ..
  mkdir test && cd test

Start a Python session (e.g., run ``python``) and try the following commands:

.. code:: python

  from pymt_heatf import HeatF
  m = HeatF()
  m.get_component_name()

You should see:

.. code:: bash

  The 2D Heat Equation

We've imported the *heat* model,
written in Fortran,
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

  bmi-test pymt_heatf:HeatF --config-file=config.txt --root-dir=. -vvv

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
to the directory ``pymt_heatf``.
Under this directory,
the *babelizer* created a directory for *heat* model metadata,
``meta/HeatF``.
Change back to the ``pymt_heatf`` directory
and view the current metadata:

.. code:: bash

  cd ../pymt_heatf
  ls meta/HeatModel/

which gives:

.. code:: bash

  api.yaml

The file ``api.yaml`` is automatically generated by the *babelizer*.
To complete the description of the *heat* model,
other metadata files are needed, including:

* :download:`info.yaml <examples/fortran/info.yaml>`
* :download:`run.yaml <examples/fortran/run.yaml>`
* a :download:`templated model configuration file <examples/fortran/heat.txt>`
* :download:`parameters.yaml <examples/fortran/parameters.yaml>`

`Descriptions`_ of these files and their roles
are given in the CSDMS Model Metadata repository.
Download each of the files using the links in the list above
and place them in the ``pymt_heatf/meta/HeatF`` directory
alongside ``api.yaml``.
The structure of the ``meta`` directory should look like:

.. code:: bash

  meta/
  └── HeatF/
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

  from pymt.models import HeatF
  m = HeatF()
  m.name

You should see:

.. code:: bash

  The 2D Heat Equation

A longer example,
:download:`pymt_heatf_ex.py <examples/fortran/pymt_heatf_ex.py>`,
is included in the documentation.
For easy viewing, it's reproduced here verbatim:

.. include:: examples/fortran/pymt_heatf_ex.py
   :literal:

:download:`Download <examples/fortran/pymt_heatf_ex.py>` this Python script,
make sure we're still in the `test` directory we just created,
then run it with:

.. code:: bash

  python pymt_heatf_ex.py


Summary
-------

Using the *babelizer*, we wrapped the *heat* model, which is written in Fortran.
It can now be called as a *pymt* component in Python.

The steps for wrapping a model with the *babelizer* outlined in this example
can also be applied to models written in C (:doc:`see the example <example-c>`)
and C++.


..
   Links

.. _bmi-example-fortran: https://github.com/csdms/bmi-example-fortran
.. _instructions: https://github.com/csdms/bmi-example-c/blob/master/README.md
.. _Developer Command Prompt: https://docs.microsoft.com/en-us/dotnet/framework/tools/developer-command-prompt-for-vs
.. _bmi-tester: https://bmi-tester.readthedocs.io
.. _Python Modeling Tool: https://pymt.readthedocs.io
.. _CSDMS Model Metadata: https://github.com/csdms/model_metadata
.. _Descriptions: https://github.com/csdms/model_metadata/blob/develop/README.rst
