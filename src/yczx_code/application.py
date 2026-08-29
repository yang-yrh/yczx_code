"""组合根：装配配置、Provider、Agent、工具、策略、会话与事件。"""

from __future__ import annotations

from .agents.coding_agent import CodingAgent
from .core.config import AppConfig
from .core.context import Context
from .core.contracts import Provider
from .core.events import EventStream
from .core.session import SessionStore
from .providers.base import OpenAICompatibleProvider
from .providers.fake import FakeProvider
from .providers.gateway import YCZXGatewayProvider
from .safety.policy import ToolPolicy
from .tools.calculator import CalculatorTool
from .tools.registry import ToolRegistry


class Application:
    """创建配置、Provider、Agent、工具与策略的装配入口。"""

    def __init__(
        self,
        config: AppConfig,
        store: SessionStore | None = None,
        provider: Provider | None = None,
    ) -> None:
        self._config = config
        self._provider = provider if provider is not None else self._build_provider()
        self._registry = ToolRegistry()
        self._registry.register(CalculatorTool(config.workspace))
        self._policy = ToolPolicy()
        self._events = EventStream()
        self._context = Context(max_tokens=config.max_tokens)
        self._store = store
        self._agent = CodingAgent(
            name="yczx",
            provider=self._provider,
            context=self._context,
            tools=self._registry,
            policy=self._policy,
            events=self._events,
            config=self._config,
        )

    def _build_provider(self) -> OpenAICompatibleProvider:
        if self._config.provider.name == "gateway":
            return YCZXGatewayProvider(
                base_url=self._config.provider.base_url,
                api_key=self._config.provider.api_key_env,
            )
        return FakeProvider()

    def agent(self) -> CodingAgent:
        return self._agent

    def registry(self) -> ToolRegistry:
        return self._registry

    def events(self):
        """返回事件流，供远端回放或 CLI 渲染。"""
        return self._events
