#!/usr/bin/env python
import os
import pathlib
import shutil
import subprocess

from click.testing import CliRunner

from babelizer.cli import babelize


def test_babelize_init_python(tmpdir, datadir):
    runner = CliRunner()

    with tmpdir.as_cwd():
        shutil.copy(datadir / "babel.toml", ".")
        result = runner.invoke(babelize, ["init", "babel.toml"])

        assert result.exit_code == 0
        assert pathlib.Path("pymt_heatpy").exists()
        assert (pathlib.Path("pymt_heatpy") / "babel.toml").is_file()

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
