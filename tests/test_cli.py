"""Test the babelizer command-line interface"""

import sys

if sys.version_info >= (3, 11):  # pragma: no cover (PY11+)
    import tomllib
else:  # pragma: no cover (<PY311)
    import tomli as tomllib

from click.testing import CliRunner

from babelizer.cli import babelize
from babelizer.metadata import BabelMetadata


def test_help():
    runner = CliRunner()
    result = runner.invoke(babelize, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output


def test_version():
    runner = CliRunner()
    result = runner.invoke(babelize, ["--version"])
    assert result.exit_code == 0
    assert "version" in result.output


def test_defaults():
    runner = CliRunner()
    result = runner.invoke(babelize)
    assert result.exit_code == 0
    assert "Usage:" in result.output


def test_generate_help():
    runner = CliRunner()
    result = runner.invoke(babelize, ["sample-config", "--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output


def test_init_help():
    runner = CliRunner()
    result = runner.invoke(babelize, ["init", "--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output


def test_update_help():
    runner = CliRunner()
    result = runner.invoke(babelize, ["update", "--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output


def test_generate_noargs():
    runner = CliRunner()
    result = runner.invoke(babelize, ["sample-config"])
    assert result.exit_code == 0


def test_generate_gives_valid_toml():
    runner = CliRunner()
    result = runner.invoke(babelize, ["sample-config"])
    assert result.exit_code == 0

    config = tomllib.loads(result.output)
    BabelMetadata.validate(config)


def test_init_noargs():
    runner = CliRunner()
    result = runner.invoke(babelize, ["init"])
    assert result.exit_code != 0


def test_update_noargs():
    runner = CliRunner()
    result = runner.invoke(babelize, ["update"])
    assert result.exit_code != 0
