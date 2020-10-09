{{ '=' * cookiecutter.package_name | length }}
{{ cookiecutter.package_name }}
{{ '=' * cookiecutter.package_name | length }}

{% set is_open_source = cookiecutter.open_source_license != 'Not open source' -%}

{% if is_open_source %}
.. image:: https://img.shields.io/badge/CSDMS-Basic%20Model%20Interface-green.svg
        :target: https://bmi.readthedocs.io/
        :alt: Basic Model Interface

.. image:: https://img.shields.io/badge/recipe-{{ cookiecutter.package_name }}-green.svg
        :target: https://anaconda.org/conda-forge/{{ cookiecutter.package_name }}

.. image:: https://img.shields.io/travis/{{ cookiecutter.info.github_username }}/{{ cookiecutter.package_name }}.svg
        :target: https://travis-ci.org/{{ cookiecutter.info.github_username }}/{{ cookiecutter.package_name }}

.. image:: https://readthedocs.org/projects/{{ cookiecutter.package_name | replace("_", "-") }}/badge/?version=latest
        :target: https://{{ cookiecutter.package_name | replace("_", "-") }}.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
        :target: https://github.com/csdms/pymt
        :alt: Code style: black
{%- endif %}


{{ cookiecutter.info.project_short_description }}

{% if is_open_source %}
* Free software: {{ cookiecutter.open_source_license }}
* Documentation: https://{{ cookiecutter.package_name | replace("_", "-") }}.readthedocs.io.
{% endif %}

{% set mwidth = ["Component" | length] -%}
{%- for babelized_class, component in cookiecutter.components|dictsort %}
    {%- if babelized_class|length > mwidth[0] -%}
        {% set _ = mwidth.pop() -%}
        {% set _ = mwidth.append(babelized_class|length) -%}
    {%- endif -%}
{%- endfor %}
{% set max_width = mwidth[0] %}

{%- set width_col_1 = max_width -%}
{%- set width_col_2 = max_width + "`from pymt.models import `" | length -%}
{% set fmt = "%-" + max_width|string + "s" %}
{{ '=' * max_width }} {{ '=' * width_col_2 }}
{{ fmt | format("Component",) }} PyMT
{{ '=' * max_width }} {{ '=' * width_col_2 }}
{% for babelized_class, component in cookiecutter.components|dictsort %}
{{ fmt | format(babelized_class) }} `from pymt.models import {{ babelized_class }}`
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

-----------'-' * cookiecutter.package_name | length }}
Installing {{ cookiecutter.package_name }}
-----------'-' * cookiecutter.package_name | length }}

{% if cookiecutter.package_requirements -%}
Once `pymt` is installed, the dependencies of `{{ cookiecutter.package_name }}` can
be installed with:

.. code::

  conda install {{ cookiecutter.package_requirements.split(',') | join(" ") }}

{%- endif %}

To install `{{ cookiecutter.package_name }}`,

.. code::

  conda install {{ cookiecutter.package_name }}
