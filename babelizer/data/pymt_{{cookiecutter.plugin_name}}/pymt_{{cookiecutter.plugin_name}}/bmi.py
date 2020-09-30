from __future__ import absolute_import

{% set classes = [] -%}
{%- for pymt_class in cookiecutter.components -%}
    {% set _ = classes.append(pymt_class) %}
{%- endfor -%}

{%- if cookiecutter.language in ['c', 'c++', 'fortran'] %}

from .lib import {{ classes|join(', ') }}

{%- else %}
import pkg_resources

{% for pymt_class, component in cookiecutter.components %}

from {{ component.library }} import {{ component.class }} as {{ pymt_class }}

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
