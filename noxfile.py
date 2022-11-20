import os
import pathlib
import shutil
from itertools import chain

import nox

PROJECT = "babelizer"
ROOT = pathlib.Path(__file__).parent
ALL_LANGS = {"c", "cxx", "fortran", "python"}


@nox.session(venv_backend="mamba", python=["3.9", "3.10", "3.11"])
def test(session: nox.Session) -> None:
    """Run the tests."""
    session.install(".[dev,testing]")

    args = session.posargs or ["-n", "auto", "--cov", PROJECT, "-vvv"]
    if "CI" in os.environ:
        args.append("--cov-report=xml:$(pwd)/coverage.xml")
    session.run("pytest", *args)


@nox.session(
    name="test-langs",
    python=["3.9", "3.10", "3.11"],
    venv_backend="mamba",
)
@nox.parametrize("lang", ["c", "cxx", "fortran", "python"])
def test_langs(session: nox.Session, lang) -> None:
    """Run language tests."""
    build_examples(session, lang)

    session.conda_install("pip", "bmi-tester>=0.5.4")
    session.install(".[testing]")

    session.run(
        "pytest", f"external/tests/test_{lang}.py", "--disable-warnings", "-vvv"
    )


@nox.session(name="build-examples", venv_backend="mamba")
@nox.parametrize("lang", ["c", "cxx", "fortran", "python"])
def build_examples(session: nox.Session, lang):
    """Build the language examples."""
    if lang == "python":
        session.conda_install("bmipy", "make")
        session.run("make", "-C", f"external/bmi-example-{lang}", "install")
    else:
        session.conda_install(
            f"{lang}-compiler", f"bmi-{lang}", "make", "cmake", "pkg-config"
        )
        session.run(
            "cmake",
            "-S",
            f"external/bmi-example-{lang}",
            "-B",
            f"build/external/{lang}",
            f"-DCMAKE_INSTALL_PREFIX={session.env['CONDA_PREFIX']}",
        )
        session.run("make", "-C", f"build/external/{lang}", "install")


@nox.session(name="test-cli")
def test_cli(session: nox.Session) -> None:
    """Test the command line interface."""
    session.install(".")
    session.run("babelize", "--version")
    session.run("babelize", "--help")
    session.run("babelize", "init", "--help")
    session.run("babelize", "update", "--help")
    session.run("babelize", "generate", "--help")


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


@nox.session(name="build-docs", reuse_venv=True)
def build_docs(session: nox.Session) -> None:
    """Build the docs."""
    with session.chdir(ROOT):
        session.install(".[docs]")

    clean_docs(session)

    with session.chdir(ROOT):
        session.run(
            "sphinx-apidoc",
            "-e",
            "-force",
            "--no-toc",
            "--module-first",
            # "--templatedir",
            # "docs/_templates",
            "-o",
            "docs/source/api",
            "babelizer",
        )
        session.run(
            "sphinx-build",
            "-b",
            "html",
            # "-W",
            "docs/source",
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
        "docs/source/_templates",
        "-o",
        "docs/source/api",
        "babelizer",
    )
    session.run(
        "sphinx-autobuild",
        "-b",
        "dirhtml",
        "docs/source",
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

    with session.chdir(ROOT / "docs" / "source"):
        for p in pathlib.Path("api").rglob("babelizer*.rst"):
            p.unlink()
