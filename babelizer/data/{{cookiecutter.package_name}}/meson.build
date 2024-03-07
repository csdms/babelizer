project('{{ cookiecutter.package_name }}', '{{ cookiecutter.language }}', 'cython', version: '{{ cookiecutter.package_version }}')

py = import('python').find_installation(pure: false)
fc = meson.get_compiler('fortran')

python_inc = py.get_path('data') / 'include'
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
        python_inc,
        numpy_inc,
    ]
)

{% set babelized_class = cookiecutter.components|list|first -%}
# babelized_class = {{ babelized_class }}

{% set dependency_list = cookiecutter.package_requirements.split(',') -%}
deps = [
{%- for dependency in dependency_list if dependency != '' %}
    fc.find_library('{{ dependency }}'),
{%- endfor %}
]

srcs = [
    '{{ cookiecutter.package_name }}/lib/bmi_interoperability.f90',
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
)

# This is a temporary fix for editable installs.
run_command('cp', '-r', '{{ cookiecutter.package_name }}/data', 'build')
