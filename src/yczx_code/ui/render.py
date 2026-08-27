"""事件渲染端口与终端实现。"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..core.contracts import AgentEvent


class Renderer(ABC):
    """将事件渲染到终端或可观测后端。"""

    @abstractmethod
    def render(self, event: AgentEvent) -> None:
        """渲染单个事件。"""
