#! /usr/bin/env python
import pkg_resources


__version__ = pkg_resources.get_distribution("{{ cookiecutter.package_name }}").version


from .bmi import (
{%- for babelized_class, _ in cookiecutter.components|dictsort %}
    {{ babelized_class }},
{%- endfor %}
)

__all__ = [
{%- for babelized_class, _ in cookiecutter.components|dictsort %}
    "{{ babelized_class }}",
{%- endfor %}
]
