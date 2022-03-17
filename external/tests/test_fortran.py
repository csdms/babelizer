#!/usr/bin/env python
import os
import pathlib
import shutil
import subprocess

from click.testing import CliRunner

from babelizer.cli import babelize


def test_babelize_init_fortran(tmpdir, datadir):
    runner = CliRunner()

    with tmpdir.as_cwd():
        shutil.copy(datadir / "babel.toml", ".")
        result = runner.invoke(babelize, ["init", "babel.toml"])

        assert result.exit_code == 0
        assert pathlib.Path("pymt_heatf").exists()
        assert (pathlib.Path("pymt_heatf") / "babel.toml").is_file()

        try:
            result = subprocess.run(
                ["pip", "install", "-e", ".", "--no-build-isolation"],
                cwd="pymt_heatf",
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
        except subprocess.CalledProcessError as err:
            assert err.output is None, err.output

        assert result.returncode == 0

        os.mkdir("_test")
        shutil.copy(datadir / "sample.cfg", "_test/")

        try:
            result = subprocess.run(
                [
                    "bmi-test",
                    "--config-file=sample.cfg",
                    "--root-dir=.",
                    "pymt_heatf:HeatBMI",
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
