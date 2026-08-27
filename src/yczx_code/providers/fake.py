"""测试替身 Provider。"""

from __future__ import annotations

from ..core.contracts import Message, ToolCall
from .base import OpenAICompatibleProvider


class FakeProvider(OpenAICompatibleProvider):
    """返回固定回复，用于单元测试与离线开发。"""

    def __init__(self, reply: str = "ok") -> None:
        super().__init__()
        self._reply = reply

    def chat(self, messages: list[Message], tools: list[ToolCall] | None = None) -> str:
        return self._reply
