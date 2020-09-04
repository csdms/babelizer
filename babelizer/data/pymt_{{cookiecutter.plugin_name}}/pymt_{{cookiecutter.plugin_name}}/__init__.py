#! /usr/bin/env python
import pkg_resources


__version__ = pkg_resources.get_distribution("pymt_{{ cookiecutter.plugin_name }}").version


from .bmi import (
{%- for entry_point in cookiecutter.entry_points.split(',') %}
    {%- set pymt_class = entry_point.split('=')[0] -%}
    {{ pymt_class }},
{%- endfor %}
)

__all__ = [
{%- for entry_point in cookiecutter.entry_points.split(',') %}
    {%- set pymt_class = entry_point.split('=')[0] -%}
    "{{ pymt_class }}",
{%- endfor %}
]
