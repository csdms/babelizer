import contextlib
import os
import subprocess
import sys

import numpy as np
from numpy.distutils.fcompiler import new_fcompiler
from setuptools import Extension
from setuptools.command.build_ext import build_ext as _build_ext


def get_compiler_flags():
    flags = {
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

    # Locate directories under Windows %LIBRARY_PREFIX%.
    if sys.platform.startswith("win"):
        flags["include_dirs"].append(os.path.join(sys.prefix, "Library", "include"))
        flags["library_dirs"].append(os.path.join(sys.prefix, "Library", "lib"))

    return flags


def get_extension_modules():
    flags = get_compiler_flags()

    libraries = [
    {%- if cookiecutter.build.libraries -%}
    {%- for lib in cookiecutter.build.libraries %}
        "{{ lib|trim }}",{% endfor %}
    {%- endif %}
    ]

    ext_modules = [
    {%- for babelized_class, component in cookiecutter.components|dictsort %}
        Extension(
            "{{cookiecutter.package_name}}.lib.{{ babelized_class|lower }}",
            ["{{cookiecutter.package_name}}/lib/{{ babelized_class|lower }}.pyx"],
            libraries=libraries + ["{{ component.library }}"],
            {% if cookiecutter.language == 'fortran' -%}
            extra_objects=["{{cookiecutter.package_name}}/lib/bmi_interoperability.o"],
            {% endif -%}
            **flags,
        ),
    {%- endfor %}
    ]

    return ext_modules


@contextlib.contextmanager
def as_cwd(path):
    prev_cwd = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(prev_cwd)


def build_interoperability():
    compiler = new_fcompiler()
    compiler.customize()

    flags = get_compiler_flags()

    cmd = []
    cmd.append(compiler.compiler_f90[0])
    cmd.append(compiler.compile_switch)
    if sys.platform.startswith("win") is False:
        cmd.append("-fPIC")
    for include_dir in flags["include_dirs"]:
        if os.path.isabs(include_dir) is False:
            include_dir = os.path.join(sys.prefix, "include", include_dir)
        cmd.append(f"-I{include_dir}")
    cmd.append("bmi_interoperability.f90")

    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError:
        raise


class build_ext(_build_ext):

    def run(self):
        with as_cwd("{{cookiecutter.package_name}}/lib"):
            build_interoperability()
        _build_ext.run(self)
