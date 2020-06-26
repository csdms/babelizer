#! /usr/bin/env python

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
