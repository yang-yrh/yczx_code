"""MCP 服务端：把内置工具暴露给 MCP 客户端。"""

from __future__ import annotations

from ..tools.base import Tool


class MCPServer:
    """将工具注册表转换为 MCP 工具定义。"""

    @staticmethod
    def to_mcp(tool: Tool) -> dict[str, object]:
        # TODO: schema 与描述映射。
        raise NotImplementedError
