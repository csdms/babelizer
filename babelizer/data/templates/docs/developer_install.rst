.. _developer_install:

=================
Developer Install
=================

.. important::

  The following commands will install *{{ package.name }}* into your current environment. Although
  not necessary, we **highly recommend** you install *{{ package.name }}* into its own
  :ref:`virtual environment <virtual_environments>`.

If you will be modifying code or contributing new code to *{{ package.name }}*, you will first
need to get *{{ package.name }}*'s source code and then install *{{ package.name }}* from that code.

Source Install
--------------

*{{ package.name }}* is actively being developed on GitHub, where the code is freely available.
If you would like to modify or contribute code, you can either clone our
repository

.. code-block:: bash

  git clone git://github.com/pymt-lab/{{ package.name }}.git

or download the `tarball <https://github.com/{{ info.github_username }}/{{ package.name }}/tarball/master>`_
(a zip file is available for Windows users):

.. code-block:: bash

  curl -OL https://github.com/{{ info.github_username }}/{{ package.name }}/tarball/master

Once you have a copy of the source code, you can install it into your current
Python environment,

.. tab:: mamba

  .. code-block:: bash

    cd {{ package.name }}
    mamba install --file=requirements.txt
    pip install -e .

.. tab:: conda

  .. code-block:: bash

    cd {{ package.name }}
    conda install --file=requirements.txt
    pip install -e .

.. tab:: pip

  .. code-block:: bash

    cd {{ package.name }}
    pip install -e .
