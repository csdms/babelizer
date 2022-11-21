import os
import pathlib
import shutil
import sys
from itertools import chain

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

import nox

PROJECT = "babelizer"
ROOT = pathlib.Path(__file__).parent
ALL_LANGS = {"c", "cxx", "fortran", "python"}
PYTHON_VERSIONS = ["3.9", "3.10", "3.11"]


@nox.session(python=PYTHON_VERSIONS)
def test(session: nox.Session) -> None:
    """Run the tests."""
    session.install(".[dev,testing]")

    args = session.posargs or ["-n", "auto", "--cov", PROJECT, "-vvv"]
    if "CI" in os.environ:
        args.append("--cov-report=xml:$(pwd)/coverage.xml")
    session.run("pytest", *args)


@nox.session(
    name="test-langs",
    python=PYTHON_VERSIONS,
    venv_backend="mamba",
)
@nox.parametrize("lang", ["c", "cxx", "fortran", "python"])
def test_langs(session: nox.session, lang) -> None:
    datadir = ROOT / "external" / "tests" / f"test_{lang}"
    tmpdir = pathlib.Path(session.create_tmp())
    testdir = tmpdir / "_test"
    testdir.mkdir()

    package, library, config_file = _get_package_metadata(datadir)

    build_examples(session, lang)

    session.conda_install("pip", "bmi-tester>=0.5.4")
    session.install(".[testing]")

    with session.chdir(tmpdir):
        session.run(
            "babelize",
            "init",
            str(datadir / "babel.toml"),
        )

        for k, v in sorted(session.env.items()):
            session.debug(f"{k}: {v!r}")

        with session.chdir(package):
            session.run("python", "-m", "pip", "install", "-e", ".")

    with session.chdir(testdir):
        shutil.copy(datadir / config_file, ".")
        session.run(
            "bmi-test",
            f"--config-file={config_file}",
            "--root-dir=.",
            f"{package}:{library}",
            "-vvv",
        )


def _get_package_metadata(datadir):
    with open(datadir / "babel.toml", "rb") as fp:
        config = tomllib.load(fp)
    package = config["package"]["name"]
    library = list(config["library"])[0]
    config_files = [fname for fname in datadir.iterdir() if fname != "babel.toml"]
    return package, library, config_files[0]


@nox.session(name="build-examples", venv_backend="mamba")
@nox.parametrize("lang", ["c", "cxx", "fortran", "python"])
def build_examples(session: nox.Session, lang):
    """Build the language examples."""
    srcdir = ROOT / "external" / f"bmi-example-{lang}"
    builddir = pathlib.Path(session.create_tmp()) / "_build"

    if lang == "python":
        session.conda_install("bmipy", "make")
    else:
        session.conda_install(f"bmi-{lang}", "make", "cmake", "pkg-config")

    for k, v in sorted(session.env.items()):
        session.debug(f"{k}: {v!r}")

    if lang == "python":
        session.run("make", "-C", str(srcdir), "install")
    else:
        builddir.mkdir()
        with session.chdir(builddir):
            session.run(
                "cmake",
                "-S",
                str(srcdir),
                "-B",
                ".",
                f"-DCMAKE_INSTALL_PREFIX={session.env['CONDA_PREFIX']}",
            )
            session.run("make", "install")


@nox.session(name="test-cli")
@nox.session(python=PYTHON_VERSIONS)
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
