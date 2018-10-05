====={{ '=' * cookiecutter.plugin_name | length }}
pymt_{{ cookiecutter.plugin_name }}
====={{ '=' * cookiecutter.plugin_name | length }}

{% set is_open_source = cookiecutter.open_source_license != 'Not open source' -%}

{% if is_open_source %}
.. image:: https://img.shields.io/pypi/v/pymt_{{ cookiecutter.plugin_name }}.svg
        :target: https://pypi.python.org/pypi/pymt_{{ cookiecutter.plugin_name }}

.. image:: https://img.shields.io/travis/{{ cookiecutter.github_username }}/pymt_{{ cookiecutter.plugin_name }}.svg
        :target: https://travis-ci.org/{{ cookiecutter.github_username }}/pymt_{{ cookiecutter.plugin_name }}

.. image:: https://readthedocs.org/projects/pymt_{{ cookiecutter.plugin_name | replace("_", "-") }}/badge/?version=latest
        :target: https://pymt_{{ cookiecutter.plugin_name | replace("_", "-") }}.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status
{%- endif %}


{{ cookiecutter.project_short_description }}

{% if is_open_source %}
* Free software: {{ cookiecutter.open_source_license }}
* Documentation: https://{{ cookiecutter.plugin_name | replace("_", "-") }}.readthedocs.io.
{% endif %}

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

  conda create -n pymt python=3.6
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
