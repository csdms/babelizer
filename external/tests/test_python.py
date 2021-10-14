#!/usr/bin/env python
import os
import pathlib
import shutil
import subprocess

import git
import pytest
import toml
from click.testing import CliRunner

from babelizer.cli import babelize


@pytest.fixture(scope="session")
def sessiondir(tmpdir_factory):
    sdir = tmpdir_factory.mktemp("tmp")
    return sdir


@pytest.mark.dependency()
def test_babelize_init_works(tmpdir, datadir):
    runner = CliRunner(mix_stderr=False)
    with tmpdir.as_cwd():
        result = runner.invoke(babelize, ["init", str(datadir / "babel.toml")])

        assert result.stdout.strip() == str(tmpdir / "pymt_heatpy")
        assert result.exit_code == 0
        assert pathlib.Path("pymt_heatpy").exists()
        assert (pathlib.Path("pymt_heatpy") / "babel.toml").is_file()

        repo = git.Repo("pymt_heatpy")

        assert not repo.bare
        assert repo.active_branch.name == "main"


@pytest.mark.dependency(depends=["test_babelize_init_works"])
@pytest.mark.parametrize("branch", ["main", "master", "coffee", None])
def test_babelize_init_python_with_branch(tmpdir, datadir, branch):
    runner = CliRunner(mix_stderr=False)

    babel_toml = toml.load(datadir / "babel.toml")
    babel_toml["info"]["github_branch"] = branch

    if branch is None:
        babel_toml["info"].pop("github_branch", None)
        branch = "main"

    with tmpdir.as_cwd():
        with open("babel.toml", "w") as fp:
            toml.dump(babel_toml, fp)

        result = runner.invoke(babelize, ["init", "babel.toml"])

        assert result.stdout.strip() == str(tmpdir / "pymt_heatpy")
        assert result.exit_code == 0
        assert pathlib.Path("pymt_heatpy").exists()
        assert (pathlib.Path("pymt_heatpy") / "babel.toml").is_file()

        repo = git.Repo("pymt_heatpy")

        assert not repo.bare
        assert repo.active_branch.name == branch


@pytest.mark.dependency(depends=["test_babelize_init_works"])
def test_babelize_build_python_example(tmpdir, datadir):
    runner = CliRunner(mix_stderr=False)

    with tmpdir.as_cwd():
        runner.invoke(babelize, ["init", str(datadir / "babel.toml")])

    with tmpdir.as_cwd():
        try:
            result = subprocess.run(
                ["pip", "install", "-e", "."],
                cwd="pymt_heatpy",
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
        except subprocess.CalledProcessError as err:
            assert err.output is None, err.output

        assert result.returncode == 0
        assert pathlib.Path("pymt_heatpy/pymt_heatpy/data/HeatPy").exists()
        assert pathlib.Path("pymt_heatpy/pymt_heatpy/data/HeatPy/api.yaml").is_file()

        os.mkdir("_test")
        shutil.copy(datadir / "heat.yaml", "_test/")

        try:
            result = subprocess.run(
                [
                    "bmi-test",
                    "--config-file=heat.yaml",
                    "--root-dir=.",
                    "pymt_heatpy:HeatPy",
                    "-vvv",
                ],
                cwd="_test",
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
        except subprocess.CalledProcessError as err:
            assert err.output is None, err.output

        assert result.returncode == 0


@pytest.mark.dependency(depends=["test_babelize_init_works"])
def test_babelize_update_python(tmpdir, datadir):
    runner = CliRunner(mix_stderr=False)

    with tmpdir.as_cwd():
        runner.invoke(babelize, ["init", str(datadir / "babel.toml")])

    with tmpdir.as_cwd():
        result = runner.invoke(babelize, ["--cd", "pymt_heatpy", "update"])

        assert result.exit_code == 0
        assert pathlib.Path("pymt_heatpy").exists()
        assert "re-rendering" in result.stderr
