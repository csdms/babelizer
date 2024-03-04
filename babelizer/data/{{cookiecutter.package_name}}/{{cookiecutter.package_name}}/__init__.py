#! /usr/bin/env python
import importlib.metadata

__version__ = importlib.metadata.version("{{ cookiecutter.package_name }}")


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
