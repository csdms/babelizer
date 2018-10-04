#! /usr/bin/env python

import os


PROJECT_DIRECTORY = os.path.realpath(os.path.curdir)
LIB_DIRECTORY = os.path.join("pymt_{{cookiecutter.plugin_name}}", "lib")


def remove_file(filepath):
    os.remove(os.path.join(PROJECT_DIRECTORY, filepath))


def remove_folder(folderpath):
    os.rmdir(os.path.join(PROJECT_DIRECTORY, folderpath))


if __name__ == "__main__":
    {%- if cookiecutter.language == 'c' %}

    remove_file(os.path.join(LIB_DIRECTORY, "bmi.hxx"))

    {%- elif cookiecutter.language == 'c++' %}

    remove_file(os.path.join(LIB_DIRECTORY, "bmi.c"))
    remove_file(os.path.join(LIB_DIRECTORY, "bmi.h"))

    {%- elif cookiecutter.language == 'python' %}

    remove_file(os.path.join(LIB_DIRECTORY, "_bmi.pyx"))
    remove_file(os.path.join(LIB_DIRECTORY, "_bmi.pxd"))
    remove_file(os.path.join(LIB_DIRECTORY, "bmi.c"))
    remove_file(os.path.join(LIB_DIRECTORY, "bmi.h"))
    remove_file(os.path.join(LIB_DIRECTORY, "bmi.hxx"))
    remove_file(os.path.join(LIB_DIRECTORY, "__init__.py"))
    remove_folder(LIB_DIRECTORY)

    {%- endif %}

    if "Not open source" == "{{ cookiecutter.open_source_license }}":
        remove_file("LICENSE")
