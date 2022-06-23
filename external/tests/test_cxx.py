#!/usr/bin/env python
import os
import pathlib
import platform
import shutil
import subprocess
import sys

from click.testing import CliRunner

from babelizer.cli import babelize


extra_opts = []
if sys.platform.startswith("linux") and int(platform.python_version_tuple()[1]) <= 8:
    extra_opts += ["--no-build-isolation"]


def test_babelize_init_cxx(tmpdir, datadir):
    runner = CliRunner()

    with tmpdir.as_cwd():
        shutil.copy(datadir / "babel.toml", ".")
        result = runner.invoke(babelize, ["init", "babel.toml"])

        assert result.exit_code == 0
        assert pathlib.Path("pymt_heat").exists()
        assert (pathlib.Path("pymt_heat") / "babel.toml").is_file()

        try:
            result = subprocess.run(
                ["pip", "install", "-e", "."] + extra_opts,
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
