from __future__ import absolute_import

{% set classes = [] -%}
{%- for babelized_class in cookiecutter.components -%}
    {% set _ = classes.append(babelized_class) %}
{%- endfor -%}

{%- if cookiecutter.language in ['c', 'c++', 'fortran'] %}

from .lib import {{ classes|join(', ') }}

{%- else %}
import sys
if sys.version_info >= (3, 12):  # pragma: no cover (PY12+)
    import importlib.resources as importlib_resources
else:  # pragma: no cover (<PY312)
    import importlib_resources


{% for babelized_class, component in cookiecutter.components|dictsort %}

from {{ component.library }} import {{ component.entry_point }} as {{ babelized_class }}

    {%- endfor %}

    {%- for cls in classes %}
{{ cls }}.__name__ = "{{ cls }}"
{{ cls }}.METADATA = str(importlib_resources.files(__name__) / "data/{{ cls }}")
    {%- endfor %}

{%- endif %}

__all__ = [
{%- for cls in classes %}
    "{{ cls }}",
{%- endfor %}
]
