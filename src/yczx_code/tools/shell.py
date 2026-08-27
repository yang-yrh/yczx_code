"""Shell 工具（安全契约完成前保持关闭）。"""

from __future__ import annotations

from typing import Any

from .base import Tool


class ShellTool(Tool):
    """执行 Shell 命令；使用时必须最小权限、确认、审计与输出限制。"""

    name = "shell"
    description = "执行 Shell 命令。"
    read_only = False

    def run(self, arguments: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
