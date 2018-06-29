#! /usr/bin/env python

import os


PROJECT_DIRECTORY = os.path.realpath(os.path.curdir)


def remove_file(filepath):
    os.remove(os.path.join(PROJECT_DIRECTORY, filepath))


def fix_python_extensions():
    """Rename .py_ files as .py files."""
    paths = []
    for (path, _, filenames) in os.walk(PROJECT_DIRECTORY):
        for filename in filenames:
            _, ext = os.path.splitext(filename)
            if ext == '.py_':
                paths.append(os.path.join(path, filename))

    for path in paths:
        base, ext = os.path.splitext(path)
        os.rename(path, base + '.py')

    return paths


if __name__ == '__main__':
    {% if cookiecutter.language != 'c' %}

    remove_file('{{cookiecutter.module_name}}/bmi.c')

    {% endif %}

    fix_python_extensions()

    if 'Not open source' == '{{ cookiecutter.open_source_license }}':
        remove_file('LICENSE')
