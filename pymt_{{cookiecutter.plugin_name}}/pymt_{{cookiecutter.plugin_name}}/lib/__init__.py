#! /usr/bin/env python

from ._bmi import (
{%- for entry_point in cookiecutter.entry_points.split(',') %}
    {%- set pymt_class = entry_point.split('=')[0] %}
    {{ pymt_class }},
{%- endfor %}
)
