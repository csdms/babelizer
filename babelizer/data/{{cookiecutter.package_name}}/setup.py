#! /usr/bin/env python
import os
import sys
{%- if cookiecutter.language == 'fortran' %}
import contextlib
import subprocess
{%- endif -%}

{%- if cookiecutter.language in ['c', 'c++', 'fortran'] %}
import numpy as np
{% endif %}
from setuptools import Extension, find_packages, setup

{% if cookiecutter.language == 'fortran' -%}
from setuptools.command.build_ext import build_ext as _build_ext
from numpy.distutils.fcompiler import new_fcompiler
{% endif %}

{% if cookiecutter.language in ['c', 'c++', 'fortran'] -%}
common_flags = {
    "include_dirs": [
        np.get_include(),
        os.path.join(sys.prefix, "include"),
        {%- for dir in cookiecutter.build.include_dirs %}
            "{{ dir|trim }}",
        {% endfor %}
    ],
    "library_dirs": [
        {%- for libdir in cookiecutter.build.library_dirs %}
            "{{ libdir|trim }}",
        {% endfor %}
    ],
    "define_macros": [
        {%- if cookiecutter.build.define_macros -%}
        {%- for item in cookiecutter.build.define_macros %}
        {%- set key_value = item.split('=') %}
            ("{{ key_value[0]|trim }}", "{{ key_value[1]|trim }}"),{% endfor %}
        {%- endif %}
    ],
    "undef_macros": [
        {%- if cookiecutter.build.undef_macros -%}
        {%- for macro in cookiecutter.build.undef_macros %}
            "{{ macro|trim }}",{% endfor %}
        {%- endif %}
    ],
    "extra_compile_args": [
        {%- if cookiecutter.build.extra_compile_args -%}
        {%- for arg in cookiecutter.build.extra_compile_args %}
            "{{ arg|trim }}",{% endfor %}
        {%- endif %}
    ],
{%- if cookiecutter.language == 'fortran' %}
    "language": "c",
{% else %}
    "language": "{{ cookiecutter.language }}",
{% endif -%}
}

libraries = [
{%- if cookiecutter.build.libraries -%}
{%- for lib in cookiecutter.build.libraries %}
    "{{ lib|trim }}",{% endfor %}
{%- endif %}
]

# Locate directories under Windows %LIBRARY_PREFIX%.
if sys.platform.startswith("win"):
    common_flags["include_dirs"].append(os.path.join(sys.prefix, "Library", "include"))
    common_flags["library_dirs"].append(os.path.join(sys.prefix, "Library", "lib"))

ext_modules = [
{%- for babelized_class, component in cookiecutter.components|dictsort %}
    Extension(
        "{{cookiecutter.package_name}}.lib.{{ babelized_class|lower }}",
        ["{{cookiecutter.package_name}}/lib/{{ babelized_class|lower }}.pyx"],
        libraries=libraries + ["{{ component.library }}"],
        {% if cookiecutter.language == 'fortran' -%}
        extra_objects=['{{cookiecutter.package_name}}/lib/bmi_interoperability.o'],
        {% endif -%}
        **common_flags
    ),
{%- endfor %}
]

{%- endif %}

entry_points = {
    "pymt.plugins": [
{%- for babelized_class, _ in cookiecutter.components|dictsort %}
        "{{ babelized_class }}={{ cookiecutter.package_name }}.bmi:{{ babelized_class }}",
{%- endfor %}
    ]
}

{% if cookiecutter.language == 'fortran' %}
@contextlib.contextmanager
def as_cwd(path):
    prev_cwd = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(prev_cwd)


def build_interoperability():
    compiler = new_fcompiler()
    compiler.customize()

    cmd = []
    cmd.append(compiler.compiler_f90[0])
    cmd.append(compiler.compile_switch)
    if sys.platform.startswith("win") is False:
        cmd.append("-fPIC")
    for include_dir in common_flags['include_dirs']:
        if os.path.isabs(include_dir) is False:
            include_dir = os.path.join(sys.prefix, "include", include_dir)
        cmd.append('-I{}'.format(include_dir))
    cmd.append('bmi_interoperability.f90')

    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError:
        raise


class build_ext(_build_ext):

    def run(self):
        with as_cwd('{{cookiecutter.package_name}}/lib'):
            build_interoperability()
        _build_ext.run(self)

{% endif -%}


def read(filename):
    with open(filename, "r", encoding="utf-8") as fp:
        return fp.read()


long_description = u'\n\n'.join(
    [read('README.rst'), read('CREDITS.rst'), read('CHANGES.rst')]
)


setup(
    name="{{cookiecutter.package_name}}",
    author="{{cookiecutter.info.full_name}}",
    author_email="{{cookiecutter.info.email}}",
    description="PyMT plugin for {{cookiecutter.package_name}}",
    long_description=long_description,
    version="{{cookiecutter.package_version}}",
    url="https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.package_name }}",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: {{ cookiecutter.open_source_license }}",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
    ],
    keywords=["bmi", "pymt"],
    install_requires=open("requirements.txt", "r").read().splitlines(),
{%- if cookiecutter.language in ['c', 'c++', 'fortran'] %}
    setup_requires=["cython"],
    ext_modules=ext_modules,
{%- endif %}
{%- if cookiecutter.language == 'fortran' %}
    cmdclass=dict(build_ext=build_ext),
{%- endif %}
    packages=find_packages(),
    entry_points=entry_points,
    include_package_data=True,
)
