from __future__ import absolute_import

{% if cookiecutter.language == 'c' or cookiecutter.language == 'c++' -%}
from .lib import {{ cookiecutter.plugin_class }}
{%- else %}
from {{ cookiecutter.plugin_module }} import {{ cookiecutter.plugin_class }}
{%- endif %}
