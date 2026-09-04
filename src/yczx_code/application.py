"""组合根：装配配置、Provider、Agent、工具、策略、会话与事件。"""

from __future__ import annotations

from uuid import uuid4

from .agents.coding_agent import CodingAgent
from .core.config import AppConfig
from .core.context import Context
from .core.contracts import AgentResult, Provider, Role
from .core.events import EventStream
from .core.session import Session, SessionNotFoundError, SessionStore
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
        self._session: Session | None = None
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

    def session_store(self) -> SessionStore | None:
        """返回注入的会话存储端口，供会话恢复与持久化使用。"""
        return self._store

    def run(self, task: str, session_id: str | None = None) -> AgentResult:
        """执行任务，并在配置了会话存储时恢复与保存上下文。"""
        if self._store is None:
            return self._agent.run(task)

        session = self._load_or_create_session(session_id)
        self._session = session
        self._context.replace(
            [message for message in session.messages if message.role is not Role.SYSTEM]
        )
        result = self._agent.run(task)
        session.messages = self._context.messages()
        self._store.save(session)
        return result

    def session_id(self) -> str | None:
        """返回最近一次运行使用的会话 ID。"""
        return self._session.session_id if self._session is not None else None

    def _load_or_create_session(self, session_id: str | None) -> Session:
        """按 ID 读取既有会话，不存在时创建新会话。"""
        assert self._store is not None
        session_id = session_id or uuid4().hex
        try:
            return self._store.load(session_id)
        except SessionNotFoundError:
            return Session(session_id=session_id)

    def events(self):
        """返回事件流，供远端回放或 CLI 渲染。"""
        return self._events
