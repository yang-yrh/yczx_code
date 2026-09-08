"""Ollama 本地模型适配器。"""

from __future__ import annotations

import json
import logging

import openai
from openai import OpenAI

from ..core.contracts import Message, ProviderResponse, ToolSpec, ToolCall
from .base import OpenAICompatibleProvider, ProviderError


class OllamaProvider(OpenAICompatibleProvider):
    """本地 Ollama 推理后端（OpenAI-compatible /v1 端点）。"""

    def __init__(
        self,
        model: str,
        base_url: str = "http://localhost:11434/v1",
        api_key: str = "sk-ollama",  # Ollama 不需要真实 key，仅占位
        timeout: float = 120.0,
        max_retries: int = 3,
        extra_headers: dict[str, str] = None,
    ) -> None:
        super().__init__(base_url=base_url, api_key=api_key)
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.extra_headers = extra_headers or {}

        self.logger = logging.getLogger(self.__class__.__name__)

        # 初始化 OpenAI 客户端（Ollama 兼容 /v1 端点）
        self.client = OpenAI(
            base_url=self._base_url,
            api_key=self._api_key,
            timeout=self.timeout,
            max_retries=self.max_retries,
            default_headers=self.extra_headers,
        )

    def chat(
        self,
        messages: list[Message],
        tools: list[ToolSpec] | None = None,
    ) -> ProviderResponse:

        # 适配消息格式为 OpenAI 格式
        formatted_messages = [
            {
                "role": msg.role.value,
                "content": msg.content,
            }
            for msg in messages
        ]

        # 适配工具格式为 OpenAI 格式
        formatted_tools = []
        if tools:
            formatted_tools = [
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.parameters,
                    },
                }
                for tool in tools
            ]

        # 调用 Ollama API
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                tools=formatted_tools if formatted_tools else None,
                tool_choice="auto" if tools else "none",
            )

            # 解析响应
            choice = response.choices[0]
            message = choice.message

            # 提取工具调用
            tool_calls = []
            if message.tool_calls:
                for tc in message.tool_calls:
                    tool_calls.append(
                        ToolCall(
                            call_id=tc.id,
                            name=tc.function.name,
                            arguments=json.loads(tc.function.arguments),
                        )
                    )

            return ProviderResponse(
                content=message.content or "",
                tool_calls=tool_calls,
            )

        except openai.APITimeoutError as error:
            err_msg = f"Ollama 请求超时 (timeout={self.timeout}s): {error}"
            print(err_msg)
            self.logger.error(err_msg)
            raise ProviderError(err_msg) from error

        except openai.APIConnectionError as error:
            err_msg = f"无法连接到 Ollama 服务，请确认 Ollama 正在运行 (http://localhost:11434): {error}"
            print(err_msg)
            self.logger.error(err_msg)
            raise ProviderError(err_msg) from error

        except openai.APIStatusError as error:
            err_msg = f"Ollama 服务返回错误: {error.status_code} - 请确认模型 '{self.model}' 已下载 (ollama pull {self.model})"
            print(err_msg)
            self.logger.error(err_msg)
            raise ProviderError(err_msg) from error

        except openai.APIResponseValidationError as error:
            err_msg = f"Ollama 返回响应格式无效，请确认 Ollama 版本是否支持工具调用: {error}"
            print(err_msg)
            self.logger.error(err_msg)
            raise ProviderError(err_msg) from error

        except Exception as error:
            err_msg = f"调用 Ollama 未知错误: {error}"
            print(err_msg)
            self.logger.error(err_msg)
            raise ProviderError(err_msg) from error