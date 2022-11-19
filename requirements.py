#! /usr/bin/env python
import argparse
import os


def _find_tomllib():
    try:
        import tomllib
    except ModuleNotFoundError:
        import tomli as tomllib
    return tomllib


def requirements(extras):

    tomllib = _find_tomllib()

    with open("pyproject.toml", "rb") as fp:
        project = tomllib.load(fp)["project"]

    dependencies = {}
    if extras:
        optional_dependencies = project.get("optional-dependencies", {})
        for extra in extras:
            dependencies[
                f"[project.optional-dependencies.{extra}]"
            ] = optional_dependencies[extra]
    else:
        dependencies["[project.dependencies]"] = project["dependencies"]

    print("# Requirements extracted from pyproject.toml")
    for section, packages in dependencies.items():
        print(f"# {section}")
        print(os.linesep.join(packages))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract requirements information from pyproject.toml"
    )
    parser.add_argument("extras", type=str, nargs="*")
    args = parser.parse_args()

    requirements(args.extras)
