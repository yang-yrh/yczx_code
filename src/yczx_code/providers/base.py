"""Provider 公共实现与错误。"""

from __future__ import annotations

from ..core.contracts import Message, ProviderResponse, ToolSpec


class ProviderError(Exception):
    """Provider 调用错误。"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class OpenAICompatibleProvider:
    """基于 OpenAI-compatible 端点的适配器骨架，协议与超时在实现时补齐。"""

    def __init__(self, base_url: str | None = None, api_key: str | None = None) -> None:
        self._base_url = base_url
        self._api_key = api_key

    def chat(
        self,
        messages: list[Message],
        tools: list[ToolSpec] | None = None,
    ) -> ProviderResponse:
        # TODO: 请求、超时、重试与错误映射。
        raise NotImplementedError
