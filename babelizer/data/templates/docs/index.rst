.. image:: _static/logo-light.svg
   :align: center
   :scale: 15%
   :alt: {{ package.name }}
   :target: https://{{ package.name }}.readthedocs.org/
   :class: only-light

.. image:: _static/logo-dark.svg
   :align: center
   :scale: 15%
   :alt: {{ package.name }}
   :target: https://{{ package.name }}.readthedocs.org/
   :class: only-dark

.. include:: ../README.rst
   :start-after: start-intro
   :end-before: end-intro

.. toctree::
   :maxdepth: 2
   :caption: User Guide
   :hidden:

   quickstart
   usage
   API <api/{{ package.name }}>
   babel
..   contributing

.. toctree::
   :maxdepth: 2
   :caption: Contribute
   :hidden:

   developer_install
   environments
   updating
   authors
   changelog
   license
