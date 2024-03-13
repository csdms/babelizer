from setuptools import setup
{% if cookiecutter.language in ['c', 'c++', 'fortran'] %}
from setup_utils import build_ext
from setup_utils import get_extension_modules

setup(
    ext_modules=get_extension_modules(),
{%- if cookiecutter.language == 'fortran' %}
    cmdclass={"build_ext": build_ext},
{%- endif %}
)
{%- else %}
setup()
{%- endif %}
