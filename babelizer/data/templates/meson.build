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

py = import('python').find_installation(pure: false)

{%- if cookiecutter.language == 'c' %}
compiler = meson.get_compiler('c')
{%- elif cookiecutter.language == 'c++' %}
compiler = meson.get_compiler('cpp')
{%- elif cookiecutter.language == 'fortran' %}
compiler = meson.get_compiler('fortran')
{%- endif %}

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

{% set dependency_list = cookiecutter.package_requirements.split(',') -%}
deps = [
{%- for dependency in dependency_list if dependency != '' %}
    compiler.find_library('{{ dependency }}'),
{%- endfor %}
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
{%- for babelized_class in cookiecutter.components|list|sort %}
    '{{ cookiecutter.package_name }}/lib/{{ babelized_class|lower }}.pyx',
{%- endfor %}
]
py.install_sources(
    install_lib_srcs,
    subdir: '{{ cookiecutter.package_name }}/lib',
)


{%- for babelized_class, component in cookiecutter.components|dictsort %}
py.extension_module(
    '{{ babelized_class|lower }}',
    [
{%- if cookiecutter.language == 'fortran' %}
        '{{ cookiecutter.package_name }}/lib/bmi_interoperability.f90',
{%- endif %}
        '{{ cookiecutter.package_name }}/lib/{{ babelized_class|lower }}.pyx',
    ],
    dependencies: [
        dependency('{{ component.library }}', method : 'pkg-config'),
    ],
    include_directories: incs,
    install: true,
    subdir: '{{ cookiecutter.package_name }}/lib',
{%- if cookiecutter.language == 'c++' %}
    override_options : ['cython_language=cpp'],
{%- endif %}
)

install_subdir(
    'meta/{{ babelized_class }}',
    install_dir: py.get_install_dir() / '{{ cookiecutter.package_name }}/data',
)

{%- endfor %}

# This is a temporary fix for editable installs.
run_command('cp', '-r', '{{ cookiecutter.package_name }}/data', 'build')
