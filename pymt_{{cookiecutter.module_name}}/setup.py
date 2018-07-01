#! /usr/bin/env python
import os, sys

from setuptools import setup, find_packages

# from Cython.Build import cythonize
from distutils.extension import Extension
import numpy as np
import versioneer

from model_metadata.utils import get_cmdclass, get_entry_points


include_dirs = [
    np.get_include(),
    os.path.join(sys.prefix, "include"),
    {%- if cookiecutter.include_dirs -%}
    {%- for dir in cookiecutter.include_dirs.split(',') %}
        "{{ dir|trim }}",{% endfor %}
    {%- endif %}
]


libraries = [
    {%- if cookiecutter.libraries -%}
    {%- for lib in cookiecutter.libraries.split(',') %}
        "{{ lib|trim }}",{% endfor %}
    {%- endif %}
]


library_dirs = [
    {%- if cookiecutter.library_dirs -%}
    {%- for libdir in cookiecutter.library_dirs.split(',') %}
        "{{ libdir|trim }}",{% endfor %}
    {%- endif %}
]


define_macros = [
    {%- if cookiecutter.define_macros -%}
    {%- for item in cookiecutter.define_macros.split(',') %}
    {%- set key_value = item.split('=') %}
        ("{{ key_value[0]|trim }}", "{{ key_value[1]|trim }}"),{% endfor %}
    {%- endif %}
]

undef_macros = [
    {%- if cookiecutter.undef_macros -%}
    {%- for macro in cookiecutter.undef_macros.split(',') %}
        "{{ macro|trim }}",{% endfor %}
    {%- endif %}
]


extra_compile_args = [
    {%- if cookiecutter.extra_compile_args -%}
    {%- for arg in cookiecutter.extra_compile_args.split(',') %}
        "{{ arg|trim }}",{% endfor %}
    {%- endif %}
]


ext_modules = [
    Extension(
        "{{cookiecutter.module_name}}._{{cookiecutter.module_name}}",
        ["{{cookiecutter.module_name}}/_{{cookiecutter.module_name}}.pyx"],
        language="{{cookiecutter.language}}",
        include_dirs=include_dirs,
        libraries=libraries,
        library_dirs=library_dirs,
        define_macros=define_macros,
        undef_macros=undef_macros,
        extra_compile_args=extra_compile_args,
    )
]


packages = find_packages(include=["{{cookiecutter.module_name}}"])
pymt_components = [
    (
        "{{cookiecutter.class_name}}={{cookiecutter.module_name}}:{{cookiecutter.class_name}}",
        "meta",
    )
]

setup(
    name="{{cookiecutter.module_name}}",
    author="Eric Hutton",
    description="Python interface to {{cookiecutter.module_name}}",
    version=versioneer.get_version(),
    setup_requires=["cython"],
    ext_modules=ext_modules,
    packages=packages,
    cmdclass=get_cmdclass(pymt_components, cmdclass=versioneer.get_cmdclass()),
    entry_points=get_entry_points(pymt_components),
)
