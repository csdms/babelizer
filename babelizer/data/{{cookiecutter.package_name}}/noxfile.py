import os
import pathlib
import shutil
from itertools import chain

import nox

PROJECT = "{{ cookiecutter.package_name }}"
ROOT = pathlib.Path(__file__).parent
PYTHON_VERSIONS = ["3.9", "3.10", "3.11"]


@nox.session(python=PYTHON_VERSIONS, venv_backend="mamba")
def test(session: nox.Session) -> None:
    """Run the tests."""
    session.conda_install("--file", "requirements-build.txt")
    session.conda_install("--file", "requirements-library.txt")
    session.conda_install("--file", "requirements-testing.txt")

    session.install(".[testing]")

{%- for babelized_class, _ in cookiecutter.components|dictsort %}
    session.run(
        "bmi-test",
        "{{ cookiecutter.package_name }}.bmi:{{ babelized_class }}",
        "-vvv",
    )
{%- endfor %}


@nox.session(venv_backend="mamba")
def update(session: nox.Session) -> None:
    session.conda_install("babelizer")

    session.run("babelize", "update")


@nox.session
def lint(session: nox.Session) -> None:
    """Look for lint."""
    session.install("pre-commit")
    session.run("pre-commit", "run", "--all-files", "--verbose")


@nox.session
def towncrier(session: nox.Session) -> None:
    """Check that there is a news fragment."""
    session.install("towncrier")
    session.run("towncrier", "check", "--compare-with", "origin/develop")


@nox.session(name="build-requirements", reuse_venv=True)
def build_requirements(session: nox.Session) -> None:
    """Create requirements files from pyproject.toml."""
    session.install("tomli")

    with open("requirements.txt", "w") as fp:
        session.run("python", "requirements.py", stdout=fp)

    for extra in ["dev", "docs", "testing"]:
        with open(f"requirements-{extra}.txt", "w") as fp:
            session.run("python", "requirements.py", extra, stdout=fp)


@nox.session(name="build-docs", reuse_venv=True, venv_backend="mamba")
def build_docs(session: nox.Session) -> None:
    """Build the docs."""
    with session.chdir(ROOT):
        session.conda_install("--file", "requirements-library.txt")
        session.install(".[docs]")

    clean_docs(session)

    with session.chdir(ROOT):
        session.run(
            "sphinx-apidoc",
            "-e",
            "-force",
            "--no-toc",
            "--module-first",
            "-o",
            "docs/api",
            "{{ cookiecutter.package_name }}",
        )
        session.run(
            "sphinx-build",
            "-b",
            "html",
            "docs",
            "build/html",
        )


@nox.session(name="live-docs", reuse_venv=True)
def live_docs(session: nox.Session) -> None:
    """Build the docs with sphinx-autobuild"""
    session.install("sphinx-autobuild")
    session.install(".[docs]")
    session.run(
        "sphinx-apidoc",
        "-e",
        "-force",
        "--no-toc",
        "--module-first",
        "--templatedir",
        "docs/_templates",
        "-o",
        "docs/api",
        "{{ cookiecutter.package_name }}",
    )
    session.run(
        "sphinx-autobuild",
        "-b",
        "dirhtml",
        "docs",
        "build/html",
        "--open-browser",
    )


@nox.session
def build(session: nox.Session) -> None:
    """Build sdist and wheel dists."""
    session.install("pip")
    session.install("wheel")
    session.install("setuptools")
    session.run("python", "--version")
    session.run("pip", "--version")
    session.run(
        "python", "setup.py", "bdist_wheel", "sdist", "--dist-dir", "./wheelhouse"
    )


@nox.session
def release(session):
    """Tag, build and publish a new release to PyPI."""
    session.install("zest.releaser[recommended]")
    session.install("zestreleaser.towncrier")
    session.run("fullrelease")


@nox.session
def publish_testpypi(session):
    """Publish wheelhouse/* to TestPyPI."""
    session.run("twine", "check", "wheelhouse/*")
    session.run(
        "twine",
        "upload",
        "--skip-existing",
        "--repository-url",
        "https://test.pypi.org/legacy/",
        "wheelhouse/*.tar.gz",
    )


@nox.session
def publish_pypi(session):
    """Publish wheelhouse/* to PyPI."""
    session.run("twine", "check", "wheelhouse/*")
    session.run(
        "twine",
        "upload",
        "--skip-existing",
        "wheelhouse/*.tar.gz",
    )


@nox.session(python=False)
def clean(session):
    """Remove all .venv's, build files and caches in the directory."""
    shutil.rmtree("build", ignore_errors=True)
    shutil.rmtree("wheelhouse", ignore_errors=True)
    shutil.rmtree(f"{PROJECT}.egg-info", ignore_errors=True)
    shutil.rmtree(".pytest_cache", ignore_errors=True)
    shutil.rmtree(".venv", ignore_errors=True)
    for p in chain(ROOT.rglob("*.py[co]"), ROOT.rglob("__pycache__")):
        if p.is_dir():
            p.rmdir()
        else:
            p.unlink()


@nox.session(python=False, name="clean-docs")
def clean_docs(session: nox.Session) -> None:
    """Clean up the docs folder."""
    with session.chdir(ROOT / "build"):
        if os.path.exists("html"):
            shutil.rmtree("html")

    with session.chdir(ROOT / "docs"):
        for p in pathlib.Path("api").rglob("{{ cookiecutter.package_name }}*.rst"):
            p.unlink()
