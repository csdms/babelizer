#! /usr/bin/env python

{% set classes = [] -%}
{%- for pymt_class, _ in cookiecutter.components|dictsort -%}
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
