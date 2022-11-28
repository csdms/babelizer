{% set classes = [] -%}
{%- for babelized_class in cookiecutter.components -%}
    {% set _ = classes.append(babelized_class) %}
{%- endfor -%}

{%- if cookiecutter.language in ['c', 'c++', 'fortran'] %}

from .lib import {{ classes|join(', ') }}

{%- else %}
import pkg_resources

{% for babelized_class, component in cookiecutter.components|dictsort %}

from {{ component.library }} import {{ component.entry_point }} as {{ babelized_class }}

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
