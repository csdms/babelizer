#! /usr/bin/env python
from setuptools import setup, find_packages
import versioneer


install_requires = [
    "pyyaml",
    "jinja2",
    "cookiecutter",
    "six",
    "scripting",
]


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
    entry_points={
        'console_scripts': [
            'bmi-wrap=bmi_wrap.cli.main_wrap:main',
        ],
        'bmi.plugins': [
            'bmi_wrap=bmi_wrap.cli.main:configure_parser_wrap',
        ],
    },
)
