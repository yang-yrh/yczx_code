"""燕中统一 API 网关适配器。"""

from __future__ import annotations

import json
import logging

import openai
from openai import OpenAI

from ..core.contracts import Message, ProviderResponse, ToolSpec, ToolCall
from .base import OpenAICompatibleProvider, ProviderError


class YCZXGatewayProvider(OpenAICompatibleProvider):
    """通过燕中统一网关调用模型，使用网关颁发的主体凭据。"""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        timeout: float = 120.0,
        max_retries: int = 3,
        extra_headers: dict[str, str] = None,
    ) -> None:
        super().__init__(base_url=base_url, api_key=api_key)
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.extra_headers = extra_headers or {}

        self.logger = logging.getLogger(self.__class__.__name__)  # 创建基础日志

        # 初始化 OpenAI 客户端
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
        # TODO: 接入燕中网关、稳定错误契约与上游追踪

        # 消息，工具适配OpenAI
        formatted_messages = [
            {
                "role": msg.role.value,
                "content": msg.content,
            }
            for msg in messages
        ]

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

        # 调用 OpenAI API
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                tools=formatted_tools,
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

        except openai.APIConnectionError as error:
            err_link = f"连接模型接口失败: {error}"
            print(err_link)
            self.logger.error(err_link)
            raise ProviderError(err_link) from error

        except openai.APIStatusError as error:
            err_status = f"接口返回错误: {error.status_code} \n请检查 Key、余额和模型名"
            print(err_status)
            self.logger.error(err_status)
            raise ProviderError(err_status) from error

        except Exception as error:
            err_other = f"调用 LLM 出现未知错误: {error}"
            print(err_other)
            self.logger.error(err_other)
            raise ProviderError(err_other) from error