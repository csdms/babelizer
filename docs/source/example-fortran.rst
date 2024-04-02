Example: Wrapping a Fortran model
=================================

In this example, we'll use the *babelizer*
to wrap the *heat* model from the `bmi-example-fortran`_ repository,
allowing it to be run in Python.
The model and its BMI are written in Fortran.
To simplify package management in the example,
we'll use :term:`conda`.
We'll also use :term:`git` to obtain the model source code.

This is a somewhat long example.
To break it up,
here are the steps we'll take:

#. Create a :term:`conda environment` that includes software to compile the
   model and wrap it with the *babelizer*
#. Clone the `bmi-example-fortran`_ repository from GitHub and build the
   *heat* model from source
#. Create a *babelizer* input file describing the *heat* model
#. Run the *babelizer* to generate Python bindings, then build the bindings
#. Show the *heat* model running in Python through *pymt*

Before we begin,
create a directory to hold our work:

.. code:: bash

  $ mkdir build && cd build

This directory is a starting point;
we'll make new directories under it as we proceed through the example.
In the end,
the first level of the directory structure under ``build`` should look like this:

.. code::

  .
  ├── babel_heatf.toml
  ├── bmi-example-fortran
  │   └── ...
  ├── environment-fortran.yml
  ├── pymt_heatf
  │   └── ...
  └── test
      └── ...

Set up a conda environment
--------------------------

Start by setting up a :term:`conda environment` that includes the *babelizer*,
as well as a toolchain to build and install the model.
The necessary packages are listed in the conda environment file
:download:`environment-fortran.yml`:

.. include:: environment-fortran.yml
   :literal:

:download:`Download <environment-fortran.yml>` this file
and create the new environment with:

.. code:: bash

  $ conda env create --file=environment-fortran.yml

When this command completes,
activate the environment
(on Linux and macOS, you may have to use ``source`` instead of ``conda``):

.. code:: bash

  $ conda activate wrap

The *wrap* environment now contains all the dependencies needed
to build, install, and wrap the *heat* model.


Build the *heat* model from source
----------------------------------

Clone the `bmi-example-fortran`_ repository from GitHub:

.. code:: bash

  $ git clone https://github.com/csdms/bmi-example-fortran

There are general `instructions`_ in the repository for building and installing
this package on Linux, macOS, and Windows.
We'll augment those instructions
with the note that we're installing into the *wrap* conda environment,
so the ``CONDA_PREFIX`` environment variable
should be used to specify the install path.

Note that if you build the model with the
`Fortran Package Manager <https://fpm.fortran-lang.org/en/index.html>`_
(fpm), you will end up with a static library (`.a` on Unix, `.lib` on
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

  $ cd bmi-example-fortran
  $ mkdir _build && cd _build
  $ cmake .. -DCMAKE_INSTALL_PREFIX=$CONDA_PREFIX
  $ make install

Verify the install by testing for the existence of the module
file of the library containing the compiled *heat* model:

.. code:: bash

  $ test -f $CONDA_PREFIX/include/bmiheatf.mod ; echo $?

A return of zero indicates success.

Windows
.......

Building the *heat* model on Windows requires either:

* A Unix-like system, such as `Cygwin <https://www.cygwin.com/>`_ or
  `Windows Subsystem for Linux <https://learn.microsoft.com/en-us/windows/wsl/>`_,
  in which case you can follow the above Linux and macOS instructions.
* Microsoft Visual Studio 2017 or later, or Microsoft Build Tools for
  Visual Studio 2017 or later, in which case the following instructions should be followed.

Open the `Developer Command Prompt`_ and run:

.. code::

  > cd bmi-example-fortran
  > mkdir _build
  > cd _build
  > cmake .. ^
      -G "NMake Makefiles" ^
      -DCMAKE_INSTALL_PREFIX=%CONDA_PREFIX% ^
      -DCMAKE_BUILD_TYPE=Release
  > cmake --build . --target install --config Release

Verify the install by testing for the existence of the module
file of the library containing the compiled *heat* model:

.. code::

  > if exist %CONDA_PREFIX%\include\bmiheatf.mod echo File exists

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


Create the *babelizer* input file
---------------------------------

The *babelizer* input file provides information to the *babelizer*
about the model to be wrapped.
The input file is created with the ``babelize generate`` subcommand.

Return to our initial ``build`` directory and call ``babelize generate`` with:

.. code:: bash

  $ cd ../..
  $ babelize generate \
      --package=pymt_heatf \
      --summary="PyMT plugin for the Fortran heat model" \
      --language=fortran \
      --library=bmiheatf \
      --entry-point=bmi_heat \
      --name=HeatModel \
      --requirement="" > babel_heatf.toml

In this call,
the *babelizer* will also fill in default values;
e.g., author name, author email, GitHub username, and license.

The resulting file, :download:`babel_heatf.toml`,
will look something like this:

.. include:: babel_heatf.toml
   :literal:

For more information on the entries and sections of the *babelizer* input file,
see `Input file <./readme.html#input-file>`_.


Wrap the model with the *babelizer*
-----------------------------------

Generate Python bindings for the model with the ``babelize init`` subcommand:

.. code:: bash

  $ babelize init babel_heatf.toml

The results are placed in a new directory, ``pymt_heatf``,
under the current directory.

.. code:: bash

  $ ls -aF pymt_heatf
  ./            .gitignore        recipe/
  ../           LICENSE           requirements-build.txt
  babel.toml    Makefile          requirements-library.txt
  CHANGES.rst   MANIFEST.in       requirements-testing.txt
  CREDITS.rst   meta/             requirements.txt
  docs/         pymt_heatf/       setup.cfg
  .git/         pyproject.toml    setup.py
  .github/      README.rst

Before we can build the Python bindings,
we must ensure that the dependencies required by the toolchain,
as well as any required by the model,
as specified in the *babelizer* input file (none in this case),
are satisfied.

Change to the ``pymt_heatf`` directory and install dependencies
into the conda environment:

.. code:: bash

  $ cd pymt_heatf
  $ conda install -c conda-forge \
      --file=requirements-build.txt \
      --file=requirements-testing.txt \
      --file=requirements-library.txt \
      --file=requirements.txt

Now build the Python bindings with:

.. code:: bash

  $ make install

This command sets off a long list of messages,
at the end of which you'll hopefully see:

.. code:: bash

  Successfully installed pymt-heatf-0.1

Internally, this uses `pip` to install the Python
package in editable mode.

Pause a moment to see what we've done.
Change back to the initial ``build`` directory,
make a new ``test`` directory,
and change to it:

.. code:: bash

  $ cd ..
  $ mkdir test && cd test

Start a Python session (e.g. run ``python``) and try the following commands:

.. code:: python

  >>> from pymt_heatf import HeatModel
  >>> m = HeatModel()
  >>> m.get_component_name()
  'The 2D Heat Equation'

We've imported the *heat* model,
written in Fortran,
into Python!
Exit the Python session (e.g. type ``exit()``)

At this point,
it's a good idea to run the *bmi-tester* (`GitHub repo <bmi-tester>`_)
over the model.
The *bmi-tester* exercises each BMI method exposed through Python,
ensuring it works correctly.
However, before running the *bmi-tester*,
one last piece of information is needed.
Like all models equipped with a BMI,
*heat* uses a :term:`configuration file` to specify initial parameter values.
Create a configuration file for *heat* at the command line with:

.. code:: bash

  $ echo "1.5, 8.0, 6, 5" > config.txt

or download the file :download:`config.txt <examples/config.txt>`
(making sure to place it in the ``test`` directory).

Run the *bmi-tester*:

.. code:: bash

  $ bmi-test pymt_heatf:HeatModel --config-file=config.txt --root-dir=. -vvv

This command sets off a long list of messages,
ending with

.. code:: bash

  🎉 All tests passed!

if everything has been built correctly.


Add metadata to make a *pymt* component
---------------------------------------

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
``meta/HeatModel``.
Change back to the ``pymt_heatf`` directory
and view the current metadata:

.. code:: bash

  $ cd ../pymt_heatf
  $ ls meta/HeatModel/
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
and place them in the ``pymt_heatf/meta/HeatModel`` directory
alongside ``api.yaml``.

Next, install *pymt*:

.. code:: bash

  $ conda install -c conda-forge pymt

Then start a Python session and show that the *heat* model
can be called through *pymt*:

.. code:: python

  >>> from pymt.models import HeatModel
  >>> m = HeatModel()
  >>> m.name
  'The 2D Heat Equation'

A longer example,
:download:`pymt_heatc_ex.py <examples/pymt_heatc_ex.py>`,
is included in the documentation.
For easy viewing, it's reproduced here verbatim:

.. include:: examples/pymt_heatc_ex.py
   :literal:

:download:`Download <examples/pymt_heatc_ex.py>` this Python script,
make sure we're still in the `test` directory we just created,
then run it with:

.. code:: bash

  $ python pymt_heatc_ex.py

Note that here we are actually running the Python script that
was developed for the :doc:`C example <example-c>`, not Fortran.
That is one of the powerful things about wrapping your
BMI-enabled model and accessing it via PyMT - it provides a
standardised interface, regardless of the underlying model
and the language it was written in.


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
.. _bmi-tester: https://github.com/csdms/bmi-tester
.. _Python Modeling Tool: https://pymt.readthedocs.io
.. _CSDMS Model Metadata: https://github.com/csdms/model_metadata
.. _Descriptions: https://github.com/csdms/model_metadata/blob/develop/README.rst
