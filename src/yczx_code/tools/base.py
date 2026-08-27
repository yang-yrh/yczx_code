"""工具抽象：名称、说明、schema、权限与并发标记。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ToolError(Exception):
    """工具执行或注册错误。"""


class Tool(ABC):
    """自包含工具模块，须声明权限、只读与并发行为。"""

    name: str
    description: str
    parameters: dict[str, object] = {}
    read_only: bool = True
    concurrency_safe: bool = False

    def __init__(self, workspace_root: Any) -> None:
        self._workspace = workspace_root

    @abstractmethod
    def run(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """执行工具并返回结构化结果。"""
