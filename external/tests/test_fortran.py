#!/usr/bin/env python
import os
import pathlib
import shutil
import subprocess
import tomlkit as toml

from click.testing import CliRunner

from babelizer.cli import babelize


def test_babelize_init_fortran_default_instances(tmpdir, datadir):
    runner = CliRunner()

    with tmpdir.as_cwd():
        shutil.copy(datadir / "babel.toml", ".")
        result = runner.invoke(babelize, ["init", "babel.toml"])

        assert result.exit_code == 0
        assert pathlib.Path("pymt_heatf").exists()
        assert (pathlib.Path("pymt_heatf") / "babel.toml").is_file()

        with open("pymt_heatf/babel.toml", "r") as fp:
            meta = toml.parse(fp.read())

        assert "max_instances" in meta["build"]
        assert meta["build"]["max_instances"] == 8


def test_babelize_init_fortran_user_instances(tmpdir, datadir):
    runner = CliRunner()

    with tmpdir.as_cwd():
        shutil.copy(datadir / "user-instances.toml", ".")
        result = runner.invoke(babelize, ["init", "user-instances.toml"])

        assert result.exit_code == 0
        assert pathlib.Path("pymt_heatf").exists()
        assert (pathlib.Path("pymt_heatf") / "babel.toml").is_file()

        with open("pymt_heatf/babel.toml", "r") as fp:
            meta = toml.parse(fp.read())

        assert "max_instances" in meta["build"]
        assert meta["build"]["max_instances"] == 32


def test_babelize_build_fortran_example(tmpdir, datadir):
    runner = CliRunner()

    with tmpdir.as_cwd():
        shutil.copy(datadir / "babel.toml", ".")
        result = runner.invoke(babelize, ["init", "babel.toml"])

        try:
            result = subprocess.run(
                ["pip", "install", "-e", "."],
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
