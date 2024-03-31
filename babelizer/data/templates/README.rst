{{ '=' * package_name | length }}
{{ package_name }}
{{ '=' * package_name | length }}

{% set is_open_source = open_source_license != 'Not open source' -%}

{% if is_open_source %}
.. image:: https://img.shields.io/badge/CSDMS-Basic%20Model%20Interface-green.svg
        :target: https://bmi.readthedocs.io/
        :alt: Basic Model Interface

.. image:: https://img.shields.io/badge/recipe-{{ package_name }}-green.svg
        :target: https://anaconda.org/conda-forge/{{ package_name }}

.. image:: https://readthedocs.org/projects/{{ package_name | replace("_", "-") }}/badge/?version=latest
        :target: https://{{ package_name | replace("_", "-") }}.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://github.com/{{ info.github_username }}/{{ package_name }}/actions/workflows/test.yml/badge.svg
        :target: https://github.com/{{ info.github_username }}/{{ package_name }}/actions/workflows/test.yml

.. image:: https://github.com/{{ info.github_username }}/{{ package_name }}/actions/workflows/flake8.yml/badge.svg
        :target: https://github.com/{{ info.github_username }}/{{ package_name }}/actions/workflows/flake8.yml

.. image:: https://github.com/{{ info.github_username }}/{{ package_name }}/actions/workflows/black.yml/badge.svg
        :target: https://github.com/{{ info.github_username }}/{{ package_name }}/actions/workflows/black.yml
{%- endif %}


.. start-intro

This project provides a wrapped version (using the `babelizer <https://babelizer.readthedocs.io>`_ tool)
of components within the following following libraries that expose a Basic Model Interface.
This allows these components to be imported and used within
Python and the Python Modeling Toolkit, PyMT.

.. list-table::
  :header-rows: 1
  :width: 90%
  :widths: auto

  * - Library
    - Component
    - PyMT
  {% for babelized_class, component in components|dictsort -%}
  * - {{ component.library }}
    - :class:`~{{ package_name }}.{{ babelized_class }}`
    -
      .. code-block:: pycon

        >>> from pymt.models import {{ babelized_class }}
  {%- endfor %}

.. end-intro


{% if is_open_source %}
* Free software: {{ open_source_license }}
* Documentation: https://{{ package_name | replace("_", "-") }}.readthedocs.io.
{% endif %}


Quickstart
==========

.. start-quickstart

To get started you will need to install the *{{ package_name }}* package.
Here are two ways to do so.

Install from conda-forge
------------------------

If the *{{ package_name }}* package is distributed on *conda-forge*, install it into your current environment with *conda*.

.. code:: bash

  conda install -c conda-forge {{ package_name }}

Install from source
-------------------

You can build and install the *{{ package_name }}* package from source using *conda* and *pip*.

First, from the source directory, install package dependencies into your current environment with *conda*.

.. code:: bash

  conda install -c conda-forge --file requirements.txt --file requirements-build.txt --file requirements-library.txt

Then install the package itself with *pip*.
{%- if language == 'python' %}

.. code:: bash

  pip install -e .

{%- else %}

.. code:: bash

  pip install --no-build-isolation --editable .

Note that for an editable install, the ``--no-build-isolation`` flag must be set.
{%- endif %}

.. end-quickstart

Usage
=====

.. start-usage

There are two ways to use the components provided by this package: directly through its Basic
Model Interface (BMI), or as a PyMT plugin.

A BMI is provided by each component in this package:
{%- for babelized_class, component in components|dictsort -%}
:class:`~{{ package_name}}.{{ babelized_class }}`
{% endfor %}.


{% for babelized_class, component in components|dictsort -%}

.. code-block:: pycon

  >>> from {{ package_name}} import {{ babelized_class }}
  >>> model = {{ babelized_class }}()
  >>> model.get_component_name()  # Get the name of the component
  >>> model.get_output_var_names()  # Get a list of the component's output variables

The PyMT provides a more Pythonic and convenient way to use the component,

.. code-block:: pycon

  >>> from pymt.models import {{ babelized_class }}
  >>> model = {{ babelized_class }}()
  >>> model.component_name
  >>> model.output_var_names

{% endfor %}


.. note::

  If you will be using this project's components through the PyMT, you will first need to install
  PyMT. This can be done using either *mamba* or *conda*.

  .. tab:: mamba

    .. code-block:: bash

      mamba install pymt -c conda-forge

  .. tab:: conda

      .. code-block:: bash

        conda install pymt -c conda-forge


.. end-usage


Updating
========

.. start-updating

This project has been automatically generated using the `babelizer <https://babelizer.readthedocs.io>`_ tool.
If you have made changes to the project's ``babel.toml`` file or the would like to rerender the project
with a newer version of the *babelizer*, you can do this either directly with the *babelize* command
or using *nox*.

.. warning::

  Many of the files in the project are auto-generated by the *babelizer* and so any changes that you've
  made to them will likely be lost after running the following commands.

.. tab:: nox

  .. code:: bash

    nox -s update

.. tab:: babelizer

  .. code:: bash

    babelize update


.. end-updating
