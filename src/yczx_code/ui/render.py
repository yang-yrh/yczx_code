"""事件渲染端口与终端实现。"""

from __future__ import annotations

import sys
from abc import ABC, abstractmethod

from ..core.contracts import AgentEvent


class Renderer(ABC):
    """将事件渲染到终端或可观测后端。"""

    @abstractmethod
    def render(self, event: AgentEvent) -> None:
        """渲染单个事件。"""


class TerminalRenderer(Renderer):
    """把事件流打印到终端：诊断信息走 stderr，最终回答走 stdout。"""

    def render(self, event: AgentEvent) -> None:
        payload = event.payload
        if event.type == "model_request":
            print(
                f"[model] step={payload.get('step')} tools={payload.get('tool_names')}",
                file=sys.stderr,
            )
        elif event.type == "tool_call":
            print(f"  · 调用工具 {payload.get('name')}:", payload.get("arguments"), file=sys.stderr)
        elif event.type == "tool_result":
            print(f"  · 工具结果 {payload.get('name')}: {payload.get('summary')}", file=sys.stderr)
        elif event.type == "final":
            print(payload.get("content", ""), flush=True)
