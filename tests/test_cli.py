from pathlib import Path

from typer.testing import CliRunner

from src.yczx_code import __version__
from src.yczx_code.ui.cli import app

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

def test_run_with_session(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "run",
            str(tmp_path),
            "--task",
            "1 + 2",
            "--session",
            "c1-test",
        ],
    )

    assert result.exit_code == 0
    assert "会话 ID: c1-test" in result.output

def test_run_restores_same_session(tmp_path: Path) -> None:
    first = runner.invoke(
        app,
        [
            "run",
            str(tmp_path),
            "--task",
            "1 + 2",
            "--session",
            "c1-test",
        ],
    )

    second = runner.invoke(
        app,
        [
            "run",
            str(tmp_path),
            "--task",
            "1 + 2",
            "--session",
            "c1-test",
        ],
    )

    assert first.exit_code == 0
    assert second.exit_code == 0

    assert "调用工具 calculator" in first.output
    assert "调用工具 calculator" not in second.output
    assert "会话 ID: c1-test" in second.output