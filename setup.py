#! /usr/bin/env python
from setuptools import find_packages, setup

import versioneer


setup(
    name="babelizer",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="Wrap bmi libraries with Python bindings",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Eric Hutton",
    author_email="huttone@colorado.edu",
    url="https://github.com/csdms",
    install_requires=open("requirements.txt", "r").read().splitlines(),
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "bmi-render=babelizer.cli.main_babelize:babelize",
            "babelize=babelizer.cli.main_babelize:babelize",
            "rebabelize=babelizer.cli.main_babelize:rebabelize",
        ],
    },
)
