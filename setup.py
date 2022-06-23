#! /usr/bin/env python
from setuptools import find_packages, setup


def read(filename):
    with open(filename, "r", encoding="utf-8") as fp:
        return fp.read()


def read_requirements(filename):
    return [line.strip() for line in read(filename).splitlines()]


long_description = "\n\n".join(
    [read("README.rst"), read("CREDITS.rst"), read("CHANGES.rst")]
)

install_requires = read_requirements("requirements.txt")
extras_require = {
    "tests": read_requirements("requirements-testing.txt"),
    "docs": read_requirements("requirements-docs.txt"),
    "dev": read_requirements("requirements-dev.txt"),
}


setup(
    name="babelizer",
    version="0.3.10.dev0",
    description="Wrap bmi libraries with Python bindings",
    long_description=long_description,
    python_requires=">=3.8",
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
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Code Generators",
    ],
    keywords=["bmi", "pymt"],
    install_requires=install_requires,
    extras_require=extras_require,
    packages=find_packages(),
    include_package_data=True,
    entry_points={"console_scripts": ["babelize=babelizer.cli:babelize"]},
)
