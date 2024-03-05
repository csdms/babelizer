from setuptools import setup

{%- if cookiecutter.language in ['c', 'c++', 'fortran'] %}
from setup_utils import build_ext, get_extension_modules
{% endif %}

setup(
{%- if cookiecutter.language in ['c', 'c++', 'fortran'] %}
    ext_modules=get_extension_modules(),
{%- endif %}
{%- if cookiecutter.language == 'fortran' %}
    cmdclass={"build_ext": build_ext},
{%- endif %}
)
