"""公共契约冻结测试：锁定核心类型、默认值与 Provider 端口形状。"""

from __future__ import annotations

from dataclasses import is_dataclass

import pytest

from yczx_code.core.contracts import (
    AgentEvent,
    Message,
    ProviderResponse,
    Role,
    ToolCall,
    ToolResult,
    ToolResultStatus,
)
from yczx_code.providers.base import OpenAICompatibleProvider


def test_roles_and_message_dataclass() -> None:
    """角色值稳定，消息是公开数据对象。"""
    assert is_dataclass(Message)
    assert Role.SYSTEM == "system"
    assert Role.USER == "user"
    assert Role.ASSISTANT == "assistant"
    assert Role.TOOL == "tool"

    message = Message(Role.USER, "hello")
    assert message.role == Role.USER
    assert message.content == "hello"


def test_toolcall_and_toolresult_structure() -> None:
    """工具调用与工具结果字段保持稳定。"""
    call = ToolCall(
        call_id="call_1",
        name="calculator",
        arguments={"expression": "2 + 2"},
    )
    assert call.call_id == "call_1"
    assert call.name == "calculator"
    assert isinstance(call.arguments, dict)

    result = ToolResult(
        call_id=call.call_id,
        status=ToolResultStatus.OK,
        summary="result is 4",
    )
    assert result.call_id == call.call_id
    assert result.status == ToolResultStatus.OK
    assert result.summary == "result is 4"


def test_provider_response_defaults_and_provider_interface() -> None:
    """Provider 响应默认不带工具调用，未实现的 Provider 必须明确报错。"""
    response = ProviderResponse("ok")
    assert isinstance(response.tool_calls, list)
    assert response.tool_calls == []

    provider = OpenAICompatibleProvider()
    with pytest.raises(NotImplementedError):
        provider.chat([Message(Role.USER, "hello")])


def test_agent_event_shape() -> None:
    """事件对象字段保持稳定。"""
    event = AgentEvent(
        event_id="event_1",
        type="final",
        payload={"message": "done"},
    )
    assert event.event_id == "event_1"
    assert event.type == "final"
    assert event.payload == {"message": "done"}
