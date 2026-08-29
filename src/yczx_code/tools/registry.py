"""工具注册表：名称、schema 与分发。"""

from __future__ import annotations

from .base import Tool, ToolError


class ToolRegistry:
    """工具的集中注册与发现，每个工具仍须经过统一策略。"""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        if tool.name in self._tools:
            raise ToolError(f"duplicate tool: {tool.name}")
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        return self._tools[name]

    def names(self) -> list[str]:
        return list(self._tools)

    def all(self) -> list[Tool]:
        """返回全部已注册工具。"""
        return list(self._tools.values())
