#! /usr/bin/env python
import pkg_resources


__version__ = pkg_resources.get_distribution("pymt_{{ cookiecutter.plugin_name }}").version


from .bmi import (
{%- for pymt_class, _ in cookiecutter.components|dictsort %}
    {{ pymt_class }},
{%- endfor %}
)

__all__ = [
{%- for pymt_class, _ in cookiecutter.components|dictsort %}
    "{{ pymt_class }}",
{%- endfor %}
]
