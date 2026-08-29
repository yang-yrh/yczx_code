"""命令行入口：解析参数、收集确认并渲染事件。"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from yczx_code import __version__

from ..application import Application
from ..core.config import AppConfig, ProviderConfig
from ..providers.fake import FakeProvider
from .render import TerminalRenderer

app = typer.Typer(
    name="yczx",
    help="轻量级终端 Coding Agent。",
    no_args_is_help=True,
    add_completion=False,
)


def version_callback(value: bool) -> None:
    if value:
        typer.echo(__version__)
        raise typer.Exit


@app.callback()
def cli(
    version: Annotated[
        bool | None,
        typer.Option("--version", callback=version_callback, is_eager=True, help="显示版本号。"),
    ] = None,
) -> None:
    """YCZX Code 命令行入口。"""


@app.command()
def run(
    workspace: Annotated[
        Path | None,
        typer.Argument(help="工作区目录，默认当前目录。"),
    ] = None,
    task: Annotated[
        str,
        typer.Option("--task", "-t", help="任务提示。"),
    ] = "1 + 2",
) -> None:
    """运行一次演示任务（默认使用 FakeProvider，离线可跑）。"""
    root = (workspace or Path.cwd()).resolve()
    config = AppConfig(workspace=root, provider=ProviderConfig(name="fake"))
    application = Application(config, provider=FakeProvider())
    renderer = TerminalRenderer()
    result = application.agent().run(task)
    for event in application.events().events:
        renderer.render(event)
    typer.echo("停止原因: " + result.stop_reason, err=True)


def main() -> None:
    app()
