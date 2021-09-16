#!/usr/bin/env python
import os
import pathlib
import shutil
import subprocess
import pytest
import git

from click.testing import CliRunner

from babelizer.cli import babelize


@pytest.fixture(scope="session")
def sessiondir(tmpdir_factory):
    sdir = tmpdir_factory.mktemp("tmp")
    return sdir


def test_babelize_init_python_with_user_branch(tmpdir, datadir):
    runner = CliRunner()

    with tmpdir.as_cwd():
        shutil.copy(datadir / "user-branch.toml", ".")
        result = runner.invoke(babelize, ["init", "user-branch.toml"])

        assert result.exit_code == 0
        assert pathlib.Path("pymt_heatpy").exists()
        assert (pathlib.Path("pymt_heatpy") / "babel.toml").is_file()

        repo = git.Repo("pymt_heatpy")

        assert repo.bare == False
        assert repo.active_branch.name == "coffee"


def test_babelize_init_python_with_default_branch(sessiondir, datadir):
    runner = CliRunner()

    with sessiondir.as_cwd():
        shutil.copy(datadir / "babel.toml", ".")
        result = runner.invoke(babelize, ["init", "babel.toml"])

        assert result.exit_code == 0
        assert pathlib.Path("pymt_heatpy").exists()
        assert (pathlib.Path("pymt_heatpy") / "babel.toml").is_file()

        repo = git.Repo("pymt_heatpy")

        assert repo.bare == False
        assert repo.active_branch.name == "main"


def test_babelize_build_python_example(sessiondir, datadir):
    runner = CliRunner()

    with sessiondir.as_cwd():

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


def test_babelize_update_python(sessiondir, datadir):
    runner = CliRunner()

    with sessiondir.as_cwd():
        result = runner.invoke(babelize, ["--cd", "pymt_heatpy", "update"])

        assert result.exit_code == 0
        assert pathlib.Path("pymt_heatpy").exists()
        assert "re-rendering" in result.output
