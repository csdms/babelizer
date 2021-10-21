#!/usr/bin/env python
import os
import pathlib
import shutil
import subprocess

import git
import pytest
import tomlkit as toml
from click.testing import CliRunner

from babelizer.cli import babelize


@pytest.mark.dependency()
def test_babelize_init_works(tmpdir, datadir):
    runner = CliRunner(mix_stderr=False)
    with tmpdir.as_cwd():
        result = runner.invoke(babelize, ["init", str(datadir / "babel.toml")])

        assert result.stdout.strip() == str(tmpdir / "pymt_heatf")
        assert result.exit_code == 0
        assert pathlib.Path("pymt_heatf").exists()
        assert (pathlib.Path("pymt_heatf") / "babel.toml").is_file()

        repo = git.Repo("pymt_heatf")

        assert not repo.bare


@pytest.mark.dependency(depends=["test_babelize_init_works"])
@pytest.mark.parametrize("max_instances", [8, 32, None])
def test_babelize_init_fortran_with_user_instances(tmpdir, datadir, max_instances):
    runner = CliRunner(mix_stderr=False)

    babel_toml = toml.load(datadir / "babel.toml")
    babel_toml["build"]["max_instances"] = max_instances

    if max_instances is None:
        babel_toml["build"].pop("max_instances", None)
        max_instances = 8

    with tmpdir.as_cwd():
        with open("babel.toml", "w") as fp:
            toml.dump(babel_toml, fp)

        result = runner.invoke(babelize, ["init", "babel.toml"])

        assert result.stdout.strip() == str(tmpdir / "pymt_heatf")
        assert result.exit_code == 0
        assert pathlib.Path("pymt_heatf").exists()
        assert (pathlib.Path("pymt_heatf") / "babel.toml").is_file()

        with open("pymt_heatf/babel.toml", "r") as fp:
            meta = toml.parse(fp.read())

        assert "max_instances" in meta["build"]
        assert meta["build"]["max_instances"] == max_instances


@pytest.mark.dependency(depends=["test_babelize_init_works"])
def test_babelize_build_fortran_example(tmpdir, datadir):
    runner = CliRunner(mix_stderr=False)

    with tmpdir.as_cwd():
        runner.invoke(babelize, ["init", str(datadir / "babel.toml")])

    with tmpdir.as_cwd():
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


@pytest.mark.dependency(depends=["test_babelize_init_works"])
def test_babelize_update_fortran(tmpdir, datadir):
    runner = CliRunner(mix_stderr=False)

    with tmpdir.as_cwd():
        runner.invoke(babelize, ["init", str(datadir / "babel.toml")])

    with tmpdir.as_cwd():
        result = runner.invoke(babelize, ["--cd", "pymt_heatf", "update"])

        assert result.exit_code == 0
        assert pathlib.Path("pymt_heatf").exists()
        assert "re-rendering" in result.stderr
