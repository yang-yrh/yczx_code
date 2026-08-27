"""Agent 基类：持有模型、上下文、工具与事件流；ReAct 循环由具体 Agent 实现，
当出现第二个循环策略时再抽离为独立的运行时层。"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..safety.policy import ToolPolicy
from ..tools.registry import ToolRegistry
from .config import AppConfig
from .context import Context
from .contracts import AgentResult, Provider
from .events import EventStream


class Agent(ABC):
    """Agent 公共基类，持有模型、上下文、工具与事件流。"""

    def __init__(
        self,
        name: str,
        provider: Provider,
        context: Context,
        tools: ToolRegistry,
        policy: ToolPolicy,
        events: EventStream,
        config: AppConfig,
    ) -> None:
        self.name = name
        self._provider = provider
        self._context = context
        self._tools = tools
        self._policy = policy
        self._events = events
        self._config = config

    @abstractmethod
    def run(self, task: str) -> AgentResult:
        """执行任务并返回结果。"""
