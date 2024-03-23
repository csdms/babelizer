from __future__ import annotations

import errno
import os
import re
from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from logoizer import logoize

# PROJECT_DIRECTORY = Path.cwd().resolve()


# def remove_file(filepath: Path) -> None:
#     filepath.unlink(filepath)
#     # (PROJECT_DIRECTORY / filepath).unlink(filepath)


# def remove_folder(folderpath):
#     shutil.rmtree(PROJECT_DIRECTORY / folderpath)


# def make_folder(folderpath):
#     try:
#         # (PROJECT_DIRECTORY / folderpath).mkdir(parents=True, exist_ok=True)
#         folderpath.mkdir(parents=True, exist_ok=True)
#     except OSError:
#         pass


def clean_folder(folderpath: Path, keep: Iterable[str | Path] = ()) -> None:
    keep = {str((folderpath / path).resolve()) for path in keep}
    # if keep:
    #     keep = set([str((folderpath / path).resolve()) for path in keep])
    # else:
    #     keep = set()

    # folderpath = PROJECT_DIRECTORY / folderpath
    for fname in folderpath.glob("*"):
        if not fname.is_dir() and str(fname.resolve()) not in keep:
            fname.unlink()

    try:
        folderpath.rmdir()
    except OSError as err:
        if err.errno != errno.ENOTEMPTY:
            raise


def split_file(filepath: Path, include_preamble: bool = False) -> set[str]:
    filepath = Path(filepath)
    SPLIT_START_REGEX = re.compile(r"\s*#\s*start:\s*(?P<fname>\S+)\s*")

    files = defaultdict(list)
    fname = "preamble"
    with open(filepath) as fp:
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
            print("".join(contents).strip(), file=fp)
            # fp.write("".join(contents).strip())

    return set(files)


def write_api_yaml(folderpath: Path, **kwds: str) -> Path:
    # make_folder(folderpath)
    os.makedirs(folderpath, exist_ok=True)

    # api_yaml = PROJECT_DIRECTORY / folderpath / "api.yaml"
    api_yaml = folderpath / "api.yaml"
    contents = """\
name: {package_name}
language: {language}
package: {package_name}
class: {plugin_class}
""".format(
        **kwds
    )
    with open(api_yaml, "w") as fp:
        fp.write(contents)

    return api_yaml


def remove_trailing_whitespace(path: str | Path) -> None:
    with open(path) as fp:
        lines = [line.rstrip() for line in fp]
    with open(path, "w") as fp:
        print(os.linesep.join(lines), file=fp)


def run(context: dict[str, Any]) -> None:
    PROJECT_DIRECTORY = Path.cwd().resolve()

    package_name = context["cookiecutter"]["package_name"]
    language = context["cookiecutter"]["language"]

    LIB_DIRECTORY = PROJECT_DIRECTORY / Path(package_name, "lib")

    keep = set()

    static_dir = PROJECT_DIRECTORY / "docs" / "_static"
    # make_folder(PROJECT_DIRECTORY / static_dir)
    os.makedirs(PROJECT_DIRECTORY / static_dir, exist_ok=True)

    logoize(package_name, static_dir / "logo-light.svg", light=True)
    logoize(package_name, static_dir / "logo-dark.svg", light=False)

    remove_trailing_whitespace(static_dir / "logo-dark.svg")
    remove_trailing_whitespace(static_dir / "logo-light.svg")

    if language == "c":
        keep |= {"__init__.py", "bmi.c", "bmi.h"}
        keep |= split_file(LIB_DIRECTORY / "_c.pyx", include_preamble=True)
    elif language == "c++":
        keep |= {"__init__.py", "bmi.hxx"}
        keep |= split_file(LIB_DIRECTORY / "_cxx.pyx", include_preamble=True)
    elif language == "fortran":
        keep |= {
            "__init__.py",
            "bmi.f90",
            "bmi_interoperability.f90",
            "bmi_interoperability.h",
        }
        keep |= split_file(LIB_DIRECTORY / "_fortran.pyx", include_preamble=True)

    clean_folder(LIB_DIRECTORY, keep=keep)

    # if "Not open source" == "{{ cookiecutter.open_source_license }}":
    #     remove_file("LICENSE")

    if language == "python":
        os.remove(PROJECT_DIRECTORY / "meson.build")

    datadir = Path("meta")
    package_datadir = Path(package_name) / "data"
    if not package_datadir.exists():
        package_datadir.symlink_to(".." / datadir, target_is_directory=True)

    for babelized_class in context["cookiecutter"]["components"]:
        write_api_yaml(
            PROJECT_DIRECTORY / datadir / babelized_class,
            language=language,
            plugin_class=babelized_class,
            package_name=package_name,
        )
