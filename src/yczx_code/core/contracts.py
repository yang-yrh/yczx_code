"""公共契约：跨模块传递的明确类型，供应商字段不进入这些对象。"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol


class Role(StrEnum):
    """可提交给模型的公开角色。"""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass(frozen=True)
class Message:
    """可提交给模型的公开消息。"""

    role: Role
    content: str


@dataclass(frozen=True)
class ToolCall:
    """模型发起的工具调用。"""

    call_id: str
    name: str
    arguments: dict[str, object]


class ToolResultStatus(StrEnum):
    """工具执行结果状态。"""

    OK = "ok"
    ERROR = "error"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class ToolResult:
    """工具执行结果。"""

    call_id: str
    status: ToolResultStatus
    summary: str
    data: object | None = None
    error: str | None = None


@dataclass(frozen=True)
class AgentEvent:
    """面向 CLI、日志与观测的输出事件。"""

    event_id: str
    type: str
    payload: dict[str, object]


@dataclass(frozen=True)
class AgentResult:
    """Agent 回合的终止结果。"""

    stop_reason: str
    final_answer: str
    usage: dict[str, int]


class PolicyDecision(StrEnum):
    """工具策略判定。"""

    ALLOW = "allow"
    REJECT = "reject"
    CONFIRM = "confirm"


class Provider(Protocol):
    """公共请求到公共响应的转换端口。"""

    def chat(self, messages: list[Message], tools: list[ToolCall] | None = None) -> str:
        """发送请求并返回模型回复。"""
