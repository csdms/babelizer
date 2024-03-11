project(
    '{{ cookiecutter.package_name }}',
{%- if cookiecutter.language == 'c' %}
    'c',
{%- elif cookiecutter.language == 'c++' %}
    'cpp',
{%- elif cookiecutter.language == 'fortran' %}
    'fortran',
{%- endif %}
    'cython',
    version: '{{ cookiecutter.package_version }}',
)

{%- if cookiecutter.language == 'c' %}
lang = 'c'
bmilib = 'BmiHeatC'
{%- elif cookiecutter.language == 'c++' %}
lang = 'cpp'
bmilib = 'BmiHeatCXX'
{%- elif cookiecutter.language == 'fortran' %}
lang = 'fortran'
bmilib = 'bmiheatf'
{%- endif %}

py = import('python').find_installation(pure: false)

compiler = meson.get_compiler(lang)

# python_inc = py.get_path('data') / 'include'
numpy_inc = run_command(
    py,
    [
        '-c',
        'import numpy; print(numpy.get_include())'
    ],
    check: true
).stdout().strip()
incs = include_directories(
    [
        '{{ cookiecutter.package_name }}/lib',
        # python_inc,
        numpy_inc,
    ]
)

{% set babelized_class = cookiecutter.components|list|first -%}
# babelized_class = {{ babelized_class }}

{% set dependency_list = cookiecutter.package_requirements.split(',') -%}
deps = [
{%- if cookiecutter.language in ['c', 'c++', 'fortran'] %}
    dependency(bmilib, method : 'pkg-config'),
{% endif %}
{%- for dependency in dependency_list if dependency != '' %}
    compiler.find_library('{{ dependency }}'),
{%- endfor %}
]

srcs = [
{%- if cookiecutter.language == 'fortran' %}
    '{{ cookiecutter.package_name }}/lib/bmi_interoperability.f90',
{%- endif %}
    '{{ cookiecutter.package_name }}/lib/{{ babelized_class|lower }}.pyx',
]

# Files get copied to <python directory>/site-packages/<subdir>
install_pkg_srcs = [
    '{{ cookiecutter.package_name }}/__init__.py',
    '{{ cookiecutter.package_name }}/_bmi.py',
    '{{ cookiecutter.package_name }}/_version.py',
]
py.install_sources(
    install_pkg_srcs,
    subdir: '{{ cookiecutter.package_name }}',
)
install_lib_srcs = [
    '{{ cookiecutter.package_name }}/lib/__init__.py',
    '{{ cookiecutter.package_name }}/lib/{{ babelized_class|lower }}.pyx',
]
py.install_sources(
    install_lib_srcs,
    subdir: '{{ cookiecutter.package_name }}/lib',
)

install_subdir(
    'meta/{{ babelized_class }}',
    install_dir: py.get_install_dir() / '{{ cookiecutter.package_name }}/data',
)

py.extension_module(
    '{{ babelized_class|lower }}',
    srcs,
    dependencies: deps,
    include_directories: incs,
    install: true,
    subdir: '{{ cookiecutter.package_name }}/lib',
{%- if cookiecutter.language == 'c++' %}
    override_options : ['cython_language=cpp'],
{%- endif %}
)

# This is a temporary fix for editable installs.
run_command('cp', '-r', '{{ cookiecutter.package_name }}/data', 'build')
