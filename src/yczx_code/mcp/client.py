"""MCP 客户端：连接外部服务并调用其工具。"""

from __future__ import annotations


class MCPClient:
    """连接一个 MCP server（stdio 或 http），按不可信服务对待。"""

    def __init__(self, name: str, command: list[str] | None = None, url: str | None = None) -> None:
        self.name = name
        self._command = command
        self._url = url

    def list_tools(self) -> list[object]:
        # TODO: 拉取工具定义与权限声明。
        raise NotImplementedError

    def call(self, tool: str, arguments: dict[str, object]) -> object:
        # TODO: 调用并纳入政策、沙箱与审计。
        raise NotImplementedError
