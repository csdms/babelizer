Installation
============

To install the *babelizer*, first create a new environment.
Although this isn't strictly necessary,
it isolates the installation to avoid conflicts with your base Python installation.
This can be done with *conda*:

.. code:: bash

  conda create -n babelizer python=3
  conda activate babelizer

Requirements
------------

The *babelizer* requires Python >=3.10.

Apart from Python, the *babelizer* has a number of other requirements,
all of which can be obtained through either *pip* or *conda*,
that will be automatically installed when you install the *babelizer*.

To see a full listing of the requirements,
have a look at the project's ``requirements.txt`` file.

If you are working with the source code of the *babelizer*,
you will also want to install additional dependencies
for testing, documentation, and development.
These dependencies are listed in the files

* ``requirements-dev.txt``
* ``requirements-docs.txt``
* ``requirements-testing.txt``

Stable release
--------------

The *babelizer* and its dependencies are best installed with *conda*:

.. code:: bash

  conda install -c conda-forge babelizer

From source
-----------

After downloading the the *babelizer* source code,
run *pip* from *babelizer*'s top-level directory (the one that contains *setup.py*)
to install *babelizer* into the current environment:

.. code:: bash

  pip install -e .
