#! /usr/bin/env python
import os
import sys
{%- if cookiecutter.language == 'fortran' %}
import subprocess
{%- endif -%}

{%- if cookiecutter.language in ['c', 'c++', 'fortran'] %}
import numpy as np
{% endif %}
from setuptools import Extension, find_packages, setup

{% if cookiecutter.language == 'fortran' -%}
from setuptools.command.build_ext import build_ext as _build_ext
from numpy.distutils.fcompiler import new_fcompiler
from scripting.contexts import cd
{% endif %}

{% if cookiecutter.language in ['c', 'c++', 'fortran'] -%}
common_flags = {
    "include_dirs": [
        np.get_include(),
        os.path.join(sys.prefix, "include"),
        {%- if cookiecutter.include_dirs -%}
        {%- for dir in cookiecutter.include_dirs.split(',') %}
            "{{ dir|trim }}",{% endfor %}
        {%- endif %}
    ],
    "library_dirs": [
        {%- if cookiecutter.library_dirs -%}
        {%- for libdir in cookiecutter.library_dirs.split(',') %}
            "{{ libdir|trim }}",{% endfor %}
        {%- endif %}
    ],
    "define_macros": [
        {%- if cookiecutter.define_macros -%}
        {%- for item in cookiecutter.define_macros.split(',') %}
        {%- set key_value = item.split('=') %}
            ("{{ key_value[0]|trim }}", "{{ key_value[1]|trim }}"),{% endfor %}
        {%- endif %}
    ],
    "undef_macros": [
        {%- if cookiecutter.undef_macros -%}
        {%- for macro in cookiecutter.undef_macros.split(',') %}
            "{{ macro|trim }}",{% endfor %}
        {%- endif %}
    ],
    "extra_compile_args": [
        {%- if cookiecutter.extra_compile_args -%}
        {%- for arg in cookiecutter.extra_compile_args.split(',') %}
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
{%- if cookiecutter.libraries -%}
{%- for lib in cookiecutter.libraries.split(',') %}
    "{{ lib|trim }}",{% endfor %}
{%- endif %}
]

# Locate directories under Windows %LIBRARY_PREFIX%.
if sys.platform.startswith("win"):
    common_flags["include_dirs"].append(os.path.join(sys.prefix, "Library", "include"))
    common_flags["library_dirs"].append(os.path.join(sys.prefix, "Library", "lib"))

ext_modules = [
{%- for entry_point in cookiecutter.entry_points.split(',') %}
    {%- set pymt_class = entry_point.split('=')[0] -%}
    {%- set bmi_lib, _ = entry_point.split('=')[1].split(":") %}
    Extension(
        "pymt_{{cookiecutter.plugin_name}}.lib.{{ pymt_class|lower }}",
        ["pymt_{{cookiecutter.plugin_name}}/lib/{{ pymt_class|lower }}.pyx"],
        libraries=libraries + ["{{ bmi_lib }}"],
        {% if cookiecutter.language == 'fortran' -%}
        extra_objects=['pymt_{{cookiecutter.plugin_name}}/lib/bmi_interoperability.o'],
        {% endif -%}
        **common_flags
    ),
{%- endfor %}
]

{%- endif %}

entry_points = {
    "pymt.plugins": [
{%- for entry_point in cookiecutter.entry_points.split(',') %}
    {%- set pymt_class = entry_point.split('=')[0] -%}
        "{{ pymt_class }}=pymt_{{ cookiecutter.plugin_name }}.bmi:{{ pymt_class }}",
{%- endfor %}
    ]
}

{% if cookiecutter.language == 'fortran' %}
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
        with cd('pymt_{{cookiecutter.plugin_name}}/lib'):
            build_interoperability()
        _build_ext.run(self)


cmdclass["build_ext"] = build_ext
{% endif -%}


def read(filename):
    with open(filename, "r", encoding="utf-8") as fp:
        return fp.read()


long_description = u'\n\n'.join(
    [read('README.rst'), read('CREDITS.rst'), read('CHANGES.rst')]
)


setup(
    name="pymt_{{cookiecutter.plugin_name}}",
    author="{{cookiecutter.full_name}}",
    author_email="{{cookiecutter.email}}",
    description="PyMT plugin for {{cookiecutter.plugin_name}}",
    long_description=long_description,
    version="{{cookiecutter.plugin_version}}",
    url="https://github.com/{{ cookiecutter.github_username }}/pymt_{{ cookiecutter.plugin_name }}",
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
    packages=find_packages(),
    entry_points=entry_points,
    include_package_data=True,
)
