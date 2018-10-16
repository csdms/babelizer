from __future__ import absolute_import

from pymt.framework.bmi_bridge import bmi_factory
from .bmi import (
{%- for entry_point in cookiecutter.entry_points.split(',') -%}
    {%- set plugin_module, plugin_class = entry_point.split('=')[1].split(':') -%}
    {%- if cookiecutter.language == 'c' or cookiecutter.language == 'c++' %}
        {%- set plugin_class = entry_point.split('=')[0] -%}
    {%- endif %}
    {{ plugin_class }},
{%- endfor %}
)
{% for entry_point in cookiecutter.entry_points.split(',') -%}
    {%- set pymt_class = entry_point.split('=')[0] -%}
    {%- set plugin_module, plugin_class = entry_point.split('=')[1].split(':') -%}
    {%- if cookiecutter.language == 'c' or cookiecutter.language == 'c++' %}
        {%- set plugin_class = entry_point.split('=')[0] -%}
    {%- endif %}
{{ pymt_class }} = bmi_factory({{ plugin_class }})
{%- endfor %}

del bmi_factory
