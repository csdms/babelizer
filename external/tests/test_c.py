#!/usr/bin/env python
import os
import pathlib
import platform
import shutil
import subprocess
import sys
from functools import partial

from click.testing import CliRunner

from babelizer.cli import babelize

extra_opts: list[str] = []
if sys.platform.startswith("linux") and int(platform.python_version_tuple()[1]) <= 8:
    extra_opts += ["--no-build-isolation"]

run = partial(
    subprocess.run,
    check=True,
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)


def test_babelize_init_c(tmpdir, datadir):
    runner = CliRunner()

    with tmpdir.as_cwd():
        shutil.copy(datadir / "babel.toml", ".")
        result = runner.invoke(babelize, ["init", "babel.toml"])

        assert result.exit_code == 0
        assert pathlib.Path("pymt_heat").exists()
        assert (pathlib.Path("pymt_heat") / "babel.toml").is_file()

        try:
            result = run(["pip", "install", "-e", "."] + extra_opts, cwd="pymt_heat")
        except subprocess.CalledProcessError as err:
            assert err.output is None, err.output
        assert result.returncode == 0

        os.mkdir("_test")
        shutil.copy(datadir / "config.txt", "_test/")

        try:
            result = run(
                [
                    "bmi-test",
                    "--config-file=config.txt",
                    "--root-dir=.",
                    "pymt_heat:HeatBMI",
                    "-vvv",
                ],
                cwd="_test",
            )
        except subprocess.CalledProcessError as err:
            assert err.output is None, err.output
        assert result.returncode == 0
