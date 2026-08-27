"""命令行入口：解析参数、收集确认并渲染事件。"""

from __future__ import annotations

from typing import Annotated

import typer

from yczx_code import __version__

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


def main() -> None:
    app()
