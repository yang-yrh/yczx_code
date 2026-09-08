"""工具调用流水线：执行前 hook、审批、权限、沙箱、超时；执行后改写、日志、渲染。"""

from __future__ import annotations
from typing import Any


class ToolPipeline:
    """工具调用的前后检查点，供安全与观测插件接入。"""

    def before(self, tool_name: str, arguments: dict[str, Any]) -> None:
        # TODO: 审批、权限、沙箱与超时控制。
        raise NotImplementedError

    def after(self, result: dict[str, Any]) -> dict[str, Any]:
        # TODO: 结果改写、记录与 UI 渲染。
        return result