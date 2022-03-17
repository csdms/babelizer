#!/usr/bin/env python
import os
import pathlib
import shutil
import subprocess

from click.testing import CliRunner

from babelizer.cli import babelize


def test_babelize_init_c(tmpdir, datadir):
    runner = CliRunner()

    with tmpdir.as_cwd():
        shutil.copy(datadir / "babel.toml", ".")
        result = runner.invoke(babelize, ["init", "babel.toml"])

        assert result.exit_code == 0
        assert pathlib.Path("pymt_heat").exists()
        assert (pathlib.Path("pymt_heat") / "babel.toml").is_file()

        try:
            result = subprocess.run(
                ["pip", "install", "-e", ".", "--no-build-isolation"],
                cwd="pymt_heat",
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
        except subprocess.CalledProcessError as err:
            assert err.output is None, err.output

        assert result.returncode == 0

        os.mkdir("_test")
        shutil.copy(datadir / "config.txt", "_test/")

        try:
            result = subprocess.run(
                [
                    "bmi-test",
                    "--config-file=config.txt",
                    "--root-dir=.",
                    "pymt_heat:HeatBMI",
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
