from __future__ import absolute_import

{% set classes = [] -%}
{%- for entry_point in cookiecutter.entry_points.split(',') -%}
    {%- set pymt_class = entry_point.split('=')[0] -%}
    {% set _ = classes.append(pymt_class) %}
{%- endfor -%}

{%- if cookiecutter.language in ['c', 'c++', 'fortran'] %}

from .lib import {{ classes|join(', ') }}

{%- else %}
import pkg_resources

{% for entry_point in cookiecutter.entry_points.split(',') %}
        {%- set pymt_class = entry_point.split('=')[0] -%}
        {%- set plugin_module, plugin_class = entry_point.split('=')[1].split(':') -%}

from {{ plugin_module }} import {{ plugin_class }} as {{ pymt_class }}

    {%- endfor %}

    {%- for cls in classes %}
{{ cls }}.__name__ = "{{ cls }}"
{{ cls }}.METADATA = pkg_resources.resource_filename(__name__ , "data/{{ cls }}")
    {%- endfor %}

{%- endif %}

__all__ = [
{%- for cls in classes %}
    "{{ cls }}",
{%- endfor %}
]
