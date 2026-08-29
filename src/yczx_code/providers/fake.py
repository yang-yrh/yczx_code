"""测试替身 Provider：离线模拟一次工具调用往返。"""

from __future__ import annotations

from ..core.contracts import Message, ProviderResponse, Role, ToolCall, ToolSpec
from .base import OpenAICompatibleProvider


def _is_arithmetic(text: str) -> bool:
    """判断文本是否像一条简单算术表达式。"""
    return any(ch in "+-*/" for ch in text) and any(ch.isdigit() for ch in text)


class FakeProvider(OpenAICompatibleProvider):
    """脚本化替身：第一条算术消息触发计算器调用，后续基于工具结果作答。"""

    def __init__(self) -> None:
        super().__init__()
        self._count = 0

    def chat(
        self,
        messages: list[Message],
        tools: list[ToolSpec] | None = None,
    ) -> ProviderResponse:
        self._count += 1
        last_user = next(
            (m.content for m in reversed(messages) if m.role is Role.USER),
            "",
        )
        last_tool = next(
            (m.content for m in reversed(messages) if m.role is Role.TOOL),
            None,
        )
        if last_tool is not None:
            return ProviderResponse(content=f"完成，计算结果是：{last_tool}。", tool_calls=[])
        if _is_arithmetic(last_user):
            return ProviderResponse(
                content="",
                tool_calls=[
                    ToolCall(
                        call_id="call_1",
                        name="calculator",
                        arguments={"expression": last_user.strip()},
                    )
                ],
            )
        return ProviderResponse(content=last_user or "ok", tool_calls=[])
