from __future__ import absolute_import

from pymt.framework.bmi_bridge import bmi_factory
from .bmi import {{ cookiecutter.plugin_class }}

{{cookiecutter.pymt_class}} = bmi_factory({{ cookiecutter.plugin_class }})

del bmi_factory
