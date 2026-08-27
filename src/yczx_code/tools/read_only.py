"""只读工具（当前 Preview 可用的能力范围）。"""

from __future__ import annotations

from typing import Any

from .base import Tool


class _ReadOnlyTool(Tool):
    """只读工具公共骨架，实现在使用时补齐。"""

    read_only = True

    def run(self, arguments: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


class ListDirTool(_ReadOnlyTool):
    name = "list_dir"
    description = "列出目录条目。"


class ReadFileTool(_ReadOnlyTool):
    name = "read_file"
    description = "读取文件内容。"


class SearchFilesTool(_ReadOnlyTool):
    name = "search_files"
    description = "搜索文本。"


class GetProjectRulesTool(_ReadOnlyTool):
    name = "get_project_rules"
    description = "读取项目规则。"
