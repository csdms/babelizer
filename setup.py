#! /usr/bin/env python
from setuptools import find_packages, setup


setup(
    name="babelizer",
    version="0.1.3",
    description="Wrap bmi libraries with Python bindings",
    long_description=open("README.rst", encoding="utf-8").read(),
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
