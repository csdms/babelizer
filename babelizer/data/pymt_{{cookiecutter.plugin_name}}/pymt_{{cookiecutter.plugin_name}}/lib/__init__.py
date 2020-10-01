#! /usr/bin/env python

{%- for babelized_class in cookiecutter.components -%}
from .{{ babelized_class|lower }} import {{ babelized_class }}
{%- endfor %}

__all__ = [
{%- for babelized_class in cookiecutter.components -%}
    "{{ babelized_class }}",
{%- endfor %}
]
