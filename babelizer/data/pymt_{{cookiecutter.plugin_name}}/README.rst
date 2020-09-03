====={{ '=' * cookiecutter.plugin_name | length }}
pymt_{{ cookiecutter.plugin_name }}
====={{ '=' * cookiecutter.plugin_name | length }}

{% set is_open_source = cookiecutter.open_source_license != 'Not open source' -%}

{% if is_open_source %}
.. image:: https://img.shields.io/badge/CSDMS-Basic%20Model%20Interface-green.svg
        :target: https://bmi.readthedocs.io/
        :alt: Basic Model Interface

.. image:: https://img.shields.io/badge/recipe-pymt_{{ cookiecutter.plugin_name }}-green.svg
        :target: https://anaconda.org/conda-forge/pymt_{{ cookiecutter.plugin_name }}

.. image:: https://img.shields.io/travis/{{ cookiecutter.github_username }}/pymt_{{ cookiecutter.plugin_name }}.svg
        :target: https://travis-ci.org/{{ cookiecutter.github_username }}/pymt_{{ cookiecutter.plugin_name }}

.. image:: https://readthedocs.org/projects/pymt_{{ cookiecutter.plugin_name | replace("_", "-") }}/badge/?version=latest
        :target: https://pymt_{{ cookiecutter.plugin_name | replace("_", "-") }}.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
        :target: https://github.com/csdms/pymt
        :alt: Code style: black
{%- endif %}


{{ cookiecutter.project_short_description }}

{% if is_open_source %}
* Free software: {{ cookiecutter.open_source_license }}
* Documentation: https://{{ cookiecutter.plugin_name | replace("_", "-") }}.readthedocs.io.
{% endif %}

{% set mwidth = ["Component" | length] -%}
{%- for entry_point in cookiecutter.entry_points.split(',') %}
    {%- set pymt_class = entry_point.split('=')[0] -%}
    {%- if pymt_class|length > mwidth[0] -%}
        {% set _ = mwidth.pop() -%}
        {% set _ = mwidth.append(pymt_class|length) -%}
    {%- endif -%}
{%- endfor %}
{% set max_width = mwidth[0] %}

{%- set width_col_1 = max_width -%}
{%- set width_col_2 = max_width + "`from pymt.models import `" | length -%}
{% set fmt = "%-" + max_width|string + "s" %}
{{ '=' * max_width }} {{ '=' * width_col_2 }}
{{ fmt | format("Component",) }} PyMT
{{ '=' * max_width }} {{ '=' * width_col_2 }}
{% for entry_point in cookiecutter.entry_points.split(',') %}
    {%- set pymt_class = entry_point.split('=')[0] -%}
{{ fmt | format(pymt_class) }} `from pymt.models import {{ pymt_class }}`
{% endfor -%}
{{ '=' * max_width }} {{ '=' * width_col_2 }}

---------------
Installing pymt
---------------

Installing `pymt` from the `conda-forge` channel can be achieved by adding
`conda-forge` to your channels with:

.. code::

  conda config --add channels conda-forge

*Note*: Before installing `pymt`, you may want to create a separate environment
into which to install it. This can be done with,

.. code::

  conda create -n pymt python=3
  conda activate pymt

Once the `conda-forge` channel has been enabled, `pymt` can be installed with:

.. code::

  conda install pymt

It is possible to list all of the versions of `pymt` available on your platform with:

.. code::

  conda search pymt --channel conda-forge

----------------{{ '-' * cookiecutter.plugin_name | length }}
Installing pymt_{{ cookiecutter.plugin_name }}
----------------{{ '-' * cookiecutter.plugin_name | length }}

{% if cookiecutter.plugin_requirements -%}
Once `pymt` is installed, the dependencies of `pymt_{{ cookiecutter.plugin_name }}` can
be installed with:

.. code::

  conda install {{ cookiecutter.plugin_requirements.split(',') | join(" ") }}

{%- endif %}

To install `pymt_{{ cookiecutter.plugin_name }}`,

.. code::

  conda install pymt_{{ cookiecutter.plugin_name }}
