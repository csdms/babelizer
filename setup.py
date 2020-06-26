#! /usr/bin/env python
import os
from setuptools import setup, find_packages
import versioneer


def data_files(directory):
    paths = []
    for (path, _, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join(path, filename))
    return paths


setup(
    name='babelize',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='Wrap bmi libraries with Python bindings',
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author='Eric Hutton',
    author_email='huttone@colorado.edu',
    url='https://github.com/csdms',
    install_requires=open("requirements.txt", "r").read().splitlines(),
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'bmi-wrap=babelize.cli.main_wrap:main',
            'bmi-render=babelize.cli.main_babelize:babelize',
            'babelize=babelize.cli.main_babelize:babelize',
        ],
        'bmi.plugins': [
            'babelize=babelize.cli.main:configure_parser_wrap',
        ],
    },
)
