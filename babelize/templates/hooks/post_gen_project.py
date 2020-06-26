#! /usr/bin/env python

import os


PROJECT_DIRECTORY = os.path.realpath(os.path.curdir)


def remove_file(filepath):
    os.remove(os.path.join(PROJECT_DIRECTORY, filepath))


if __name__ == '__main__':
    {% if cookiecutter.language != 'c' %}

    remove_file('{{cookiecutter.module_name}}/bmi.c')

    {% endif %}

    if 'Not open source' == '{{ cookiecutter.open_source_license }}':
        remove_file('LICENSE')
