#! /usr/bin/env python

from .bmi import (
{%- for entry_point in cookiecutter.entry_points.split(',') %}
    {%- set plugin_module, plugin_class = entry_point.split('=')[1].split(':') -%}
    {%- if cookiecutter.language == 'c' or cookiecutter.language == 'c++' %}
        {%- set plugin_class = entry_point.split('=')[0] -%}
    {%- endif %}
    {{ plugin_class }},
{%- endfor %}
)

__all__ = [
{%- for entry_point in cookiecutter.entry_points.split(',') %}
    {%- set plugin_module, plugin_class = entry_point.split('=')[1].split(':') -%}
    {%- if cookiecutter.language == 'c' or cookiecutter.language == 'c++' %}
        {%- set plugin_class = entry_point.split('=')[0] -%}
    {%- endif %}
    "{{ plugin_class }}",
{%- endfor %}
]
