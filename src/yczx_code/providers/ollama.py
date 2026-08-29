"""Ollama 本地模型适配器。"""

from __future__ import annotations

from ..core.contracts import Message, ProviderResponse, ToolSpec
from .base import OpenAICompatibleProvider


class OllamaProvider(OpenAICompatibleProvider):
    """本地 Ollama 推理后端（OpenAI-compatible /v1 端点）。"""

    def chat(
        self,
        messages: list[Message],
        tools: list[ToolSpec] | None = None,
    ) -> ProviderResponse:
        # TODO: 连接本地服务，控制离线与成本。
        raise NotImplementedError
