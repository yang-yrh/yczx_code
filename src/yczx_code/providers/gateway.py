"""燕中统一 API 网关适配器。"""

from __future__ import annotations

from ..core.contracts import Message, ToolCall
from .base import OpenAICompatibleProvider


class YCZXGatewayProvider(OpenAICompatibleProvider):
    """通过燕中统一网关调用模型，使用网关颁发的主体凭据。"""

    def chat(self, messages: list[Message], tools: list[ToolCall] | None = None) -> str:
        # TODO: 接入燕中网关、稳定错误契约与上游追踪。
        raise NotImplementedError
