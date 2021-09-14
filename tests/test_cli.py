"""Test the babelizer command-line interface"""
from click.testing import CliRunner

from babelizer.cli import babelize


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
    result = runner.invoke(babelize, ["generate", "--help"])
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
    result = runner.invoke(babelize, ["generate"])
    assert result.exit_code == 0


def test_init_noargs():
    runner = CliRunner()
    result = runner.invoke(babelize, ["init"])
    assert result.exit_code != 0


def test_update_noargs():
    runner = CliRunner()
    result = runner.invoke(babelize, ["update"])
    assert result.exit_code != 0


def test_default_branch():
    runner = CliRunner()
    result = runner.invoke(babelize, ["generate"])
    assert result.exit_code == 0
    assert "main" in result.output


def test_set_branch():
    runner = CliRunner()
    result = runner.invoke(babelize, ["generate", "--branch", "coffee/cup"])
    assert result.exit_code == 0
    assert "coffee/cup" in result.output
