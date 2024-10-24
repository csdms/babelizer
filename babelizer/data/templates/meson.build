project(
    '{{ package.name }}',
{%- if language == 'c' %}
    'c',
{%- elif language == 'c++' %}
    'cpp',
{%- elif language == 'fortran' %}
    'fortran',
{%- endif %}
    'cython',
    version: '{{ package_version }}',
)

py = import('python').find_installation(pure: false)

{%- if language == 'c' %}
compiler = meson.get_compiler('c')
{%- elif language == 'c++' %}
compiler = meson.get_compiler('cpp')
{%- elif language == 'fortran' %}
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
        '{{ package.name }}/lib',
        # python_inc,
        numpy_inc,
    ]
)

{% set dependency_list = package.requirements -%}
deps = [
{%- for dependency in dependency_list if dependency != '' %}
    compiler.find_library('{{ dependency }}'),
{%- endfor %}
]

# Files get copied to <python directory>/site-packages/<subdir>
install_pkg_srcs = [
    '{{ package.name }}/__init__.py',
    '{{ package.name }}/_bmi.py',
    '{{ package.name }}/_version.py',
]
py.install_sources(
    install_pkg_srcs,
    subdir: '{{ package.name }}',
)

install_lib_srcs = [
    '{{ package.name }}/lib/__init__.py',
{%- for babelized_class in components|list|sort %}
    '{{ package.name }}/lib/{{ babelized_class|lower }}.pyx',
{%- endfor %}
]
py.install_sources(
    install_lib_srcs,
    subdir: '{{ package.name }}/lib',
)


{%- for babelized_class, component in components|dictsort %}
py.extension_module(
    '{{ babelized_class|lower }}',
    [
{%- if language == 'fortran' %}
        '{{ package.name }}/lib/bmi_interoperability.f90',
{%- endif %}
        '{{ package.name }}/lib/{{ babelized_class|lower }}.pyx',
    ],
    dependencies: [
        dependency('{{ component.library }}', method : 'pkg-config'),
    ],
    include_directories: incs,
    install: true,
    subdir: '{{ package.name }}/lib',
{%- if language == 'c++' %}
    override_options : ['cython_language=cpp'],
{%- endif %}
)

install_subdir(
    'meta/{{ babelized_class }}',
    install_dir: py.get_install_dir() / '{{ package.name }}/data',
)

{%- endfor %}

# This is a temporary fix for editable installs.
run_command('cp', '-r', '{{ package.name }}/data', 'build')
