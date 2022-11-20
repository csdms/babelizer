#!/usr/bin/env python
import os
import pathlib
import shutil
import subprocess
from functools import partial

import pytest
from click.testing import CliRunner

from babelizer.cli import babelize


@pytest.fixture(scope="session")
def sessiondir(tmpdir_factory):
    sdir = tmpdir_factory.mktemp("tmp")
    return sdir


run = partial(
    subprocess.run,
    check=True,
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)


def test_babelize_init_python(sessiondir, datadir):
    runner = CliRunner()

    with sessiondir.as_cwd():
        shutil.copy(datadir / "babel.toml", ".")
        result = runner.invoke(babelize, ["init", "babel.toml"])

        assert result.exit_code == 0
        assert pathlib.Path("pymt_heatpy").exists()
        assert (pathlib.Path("pymt_heatpy") / "babel.toml").is_file()

        try:
            result = run(
                ["python", "-m", "pip", "install", "-e", "."],
                cwd="pymt_heatpy",
            )

        except subprocess.CalledProcessError as err:
            assert err.output is None, err.output

        assert result.returncode == 0
        assert pathlib.Path("pymt_heatpy/pymt_heatpy/data/HeatPy").exists()
        assert pathlib.Path("pymt_heatpy/pymt_heatpy/data/HeatPy/api.yaml").is_file()

        os.mkdir("_test")
        shutil.copy(datadir / "heat.yaml", "_test/")

        try:
            result = run(
                [
                    "bmi-test",
                    "--config-file=heat.yaml",
                    "--root-dir=.",
                    "pymt_heatpy:HeatPy",
                    "-vvv",
                ],
                cwd="_test",
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
