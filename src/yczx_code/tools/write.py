"""写入工具（安全契约完成前保持关闭）。"""

from __future__ import annotations

from typing import Any

from .base import Tool


class _WriteTool(Tool):
    """写入工具公共骨架；使用时必须经过操作预览与显式确认。"""

    read_only = False

    def run(self, arguments: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


class WriteFileTool(_WriteTool):
    name = "write_file"
    description = "写入或覆盖文件。"


class EditFileTool(_WriteTool):
    name = "edit_file"
    description = "编辑文件某一片段。"
