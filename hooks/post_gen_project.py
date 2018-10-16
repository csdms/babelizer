#! /usr/bin/env python

import os


PROJECT_DIRECTORY = os.path.realpath(os.path.curdir)
LIB_DIRECTORY = os.path.join("pymt_{{cookiecutter.plugin_name}}", "lib")


def remove_file(filepath):
    os.remove(os.path.join(PROJECT_DIRECTORY, filepath))


def remove_folder(folderpath):
    os.rmdir(os.path.join(PROJECT_DIRECTORY, folderpath))


def make_folder(folderpath):
    try:
        os.mkdir(os.path.join(PROJECT_DIRECTORY, folderpath))
    except OSError:
        pass


def write_api_yaml(folderpath, **kwds):
    api_yaml = os.path.join(PROJECT_DIRECTORY, folderpath, "api.yaml")
    contents = """
name: {plugin_name}
language: {language}
package: {plugin_name}
class: {plugin_class}
""".format(**kwds).strip()
    with open(api_yaml, "w") as fp:
        fp.write(contents)

    return api_yaml


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

{% for entry_point in cookiecutter.entry_points.split(',') %}
    {%- set pymt_class = entry_point.split('=')[0] %}
    make_folder(os.path.join("meta", "{{ pymt_class }}"))

    write_api_yaml(
        os.path.join("meta", "{{ pymt_class }}"),
        language="{{ cookiecutter.language }}",
        plugin_class="{{ pymt_class }}",
        plugin_name="{{ cookiecutter.plugin_name }}",
    )
{% endfor %}
