#! /usr/bin/env python
from setuptools import find_packages, setup


def read(filename):
    with open(filename, "r", encoding="utf-8") as fp:
        return fp.read()


long_description = u'\n\n'.join(
    [read('README.rst'), read('CREDITS.rst'), read('CHANGES.rst')]
)


setup(
    name="babelizer",
    version="0.2.0",
    description="Wrap bmi libraries with Python bindings",
    long_description=long_description,
    author="Eric Hutton",
    author_email="huttone@colorado.edu",
    url="https://github.com/csdms",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Code Generators",
    ],
    keywords=["bmi", "pymt"],
    install_requires=open("requirements.txt", "r").read().splitlines(),
    packages=find_packages(),
    include_package_data=True,
    entry_points={"console_scripts": ["babelize=babelizer.cli:babelize",],},
)
