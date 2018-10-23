#! /usr/bin/env python
import os
from setuptools import setup, find_packages
import versioneer


install_requires = [
    "pyyaml",
    "jinja2",
    "cookiecutter",
    "six",
    # "scripting",
]


def data_files(directory):
    paths = []
    for (path, _, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join(path, filename))
    return paths


setup(
    name='bmi_wrap',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='Wrap bmi libraries with Python bindings',
    author='Eric Hutton',
    author_email='huttone@colorado.edu',
    url='https://github.com/csdms',
    install_requires=install_requires,
    packages=find_packages(),
    package_data={'bmi_wrap': data_files('bmi_wrap/templates')},
    entry_points={
        'console_scripts': [
            'bmi-wrap=bmi_wrap.cli.main_wrap:main',
            'bmi-render=bmi_wrap.cli.main_render:main',
        ],
        'bmi.plugins': [
            'bmi_wrap=bmi_wrap.cli.main:configure_parser_wrap',
        ],
    },
)
