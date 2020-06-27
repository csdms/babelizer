#! /usr/bin/env python
import errno
import re
from collections import defaultdict
from pathlib import Path


PROJECT_DIRECTORY = Path.cwd().resolve()
LIB_DIRECTORY = Path("pymt_{{cookiecutter.plugin_name}}", "lib")


def remove_file(filepath):
    (PROJECT_DIRECTORY / filepath).unlink(filepath)


def remove_folder(folderpath):
    shutil.rmtree(PROJECT_DIRECTORY / folderpath)


def make_folder(folderpath):
    try:
        (PROJECT_DIRECTORY / folderpath).mkdir(parents=True, exist_ok=True)
    except OSError:
        pass


def clean_folder(folderpath, keep=None):
    if keep:
        keep = set([str((folderpath / path).resolve()) for path in keep])
    else:
        keep = set()

    folderpath = PROJECT_DIRECTORY / folderpath
    for fname in folderpath.glob("*"):
        if str(fname.resolve()) not in keep:
            fname.unlink()

    try:
        folderpath.rmdir()
    except OSError as err:
        if err.errno != errno.ENOTEMPTY:
            raise


def split_file(filepath, include_preamble=False):
    filepath = Path(filepath)
    SPLIT_START_REGEX = re.compile("\s*#\s*start:\s*(?P<fname>\S+)\s*")

    files = defaultdict(list)
    fname = "preamble"
    with open(filepath, "r") as fp:
        for line in fp:
            m = SPLIT_START_REGEX.match(line)
            if m:
                fname = m["fname"]
            files[fname].append(line)

    preamble = files.pop("preamble")
    folderpath = filepath.parent
    for name, contents in files.items():
        with open(folderpath / name, "w") as fp:
            if include_preamble:
                fp.write("".join(preamble))
            fp.write("".join(contents))

    return set(files)


def write_api_yaml(folderpath, **kwds):
    make_folder(folderpath)

    api_yaml = PROJECT_DIRECTORY / folderpath / "api.yaml"
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
    keep = set()

    {%- if cookiecutter.language == 'c' %}

    keep |= set(["__init__.py", "bmi.c", "bmi.h"])
    keep |= split_file(LIB_DIRECTORY / "_c.pyx", include_preamble=True)

    {%- elif cookiecutter.language == 'c++' %}

    keep |= set(["__init__.py", "bmi.hxx"])
    keep |= split_file(LIB_DIRECTORY / "_cxx.pyx", include_preamble=True)

    {%- elif cookiecutter.language == 'fortran' %}

    keep |= set(["__init__.py", "bmi.f90", "bmi_interoperability.f90",
                 "bmi_interoperability.h"])
    keep |= split_file(LIB_DIRECTORY / "_fortran.pyx", include_preamble=True)

    {%- endif %}

    clean_folder(LIB_DIRECTORY, keep=keep)

    if "Not open source" == "{{ cookiecutter.open_source_license }}":
        remove_file("LICENSE")

{% for entry_point in cookiecutter.entry_points.split(',') %}
    {%- set pymt_class = entry_point.split('=')[0] %}
    write_api_yaml(
        Path("meta", "{{ pymt_class }}"),
        language="{{ cookiecutter.language }}",
        plugin_class="{{ pymt_class }}",
        plugin_name="{{ cookiecutter.plugin_name }}",
    )
{% endfor %}
