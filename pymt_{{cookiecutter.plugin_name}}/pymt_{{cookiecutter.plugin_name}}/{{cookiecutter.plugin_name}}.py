from __future__ import absolute_import

from pymt.framework.bmi_bridge import bmi_factory
{% if cookiecutter.language == 'c' or cookiecutter.language == 'c++' -%}
from ._{{cookiecutter.plugin_module}} import {{cookiecutter.plugin_class}}
{% else %}
from {{cookiecutter.plugin_module}} import {{cookiecutter.plugin_class}}
{% endif %}


{{cookiecutter.pymt_class}} = bmi_factory({{cookiecutter.plugin_class}})

del bmi_factory
