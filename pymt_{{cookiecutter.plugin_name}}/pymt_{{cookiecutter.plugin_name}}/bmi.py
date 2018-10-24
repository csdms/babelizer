from __future__ import absolute_import

{% for entry_point in cookiecutter.entry_points.split(',') %}
    {%- set pymt_class = entry_point.split('=')[0] -%}
    {%- set plugin_module, plugin_class = entry_point.split('=')[1].split(':') -%}
    {%- if cookiecutter.language == 'c' or cookiecutter.language == 'c++' %}
from .lib import {{ pymt_class }}
    {%- else %}
from {{ plugin_module }} import {{ plugin_class }} as {{ pymt_class }}
{{ pymt_class }}.__name__ = "{{ pymt_class }}"
    {%- endif %}
{%- endfor %}
