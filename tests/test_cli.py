from pathlib import Path

from typer.testing import CliRunner

from yczx_code import __version__
from yczx_code.ui.cli import app

runner = CliRunner()


def test_help() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "轻量级终端 Coding Agent" in result.output


def test_version() -> None:
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.output.strip() == __version__


def test_run_demo(tmp_path: Path) -> None:
    result = runner.invoke(app, ["run", str(tmp_path), "--task", "1 + 2"])

    assert result.exit_code == 0
    assert "完成" in result.output
