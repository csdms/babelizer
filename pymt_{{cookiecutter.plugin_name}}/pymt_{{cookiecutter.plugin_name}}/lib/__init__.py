#! /usr/bin/env python

{% set classes = [] -%}
{%- for entry_point in cookiecutter.entry_points.split(',') -%}
    {%- set pymt_class = entry_point.split('=')[0] -%}
    {% set _ = classes.append(pymt_class) %}
{%- endfor -%}

{%- for cls in classes %}
from .{{ cls|lower }} import {{ cls }}
{%- endfor %}

__all__ = [
{%- for cls in classes %}
    "{{ cls }}",
{%- endfor %}
]
