"""Context 裁剪行为测试：优先保留系统消息与最近消息。"""

from __future__ import annotations

from yczx_code.core.context import Context
from yczx_code.core.contracts import Message, Role


def _make_msg(role: Role, content: str) -> Message:
    """创建一条测试消息。"""
    return Message(role=role, content=content)


def test_trim_preserves_system_and_recent() -> None:
    """预算不足时，优先保留系统消息与最近内容。"""
    ctx = Context(max_tokens=10)
    ctx.add(_make_msg(Role.SYSTEM, "system instruction here"))
    ctx.add(_make_msg(Role.USER, "one two three four"))
    ctx.add(_make_msg(Role.USER, "five six seven eight nine"))

    ctx.trim()
    msgs = ctx.messages()

    assert any(msg.role == Role.SYSTEM for msg in msgs)
    assert any("five" in msg.content for msg in msgs)


def test_trim_truncates_system_if_needed() -> None:
    """预算极小且只能保留系统消息时，系统消息内容应当被截断。"""
    ctx = Context(max_tokens=1)
    ctx.add(_make_msg(Role.SYSTEM, "very important system instruction"))
    ctx.add(_make_msg(Role.USER, "user message should be dropped"))

    ctx.trim()
    msgs = ctx.messages()

    assert len(msgs) == 1
    assert msgs[0].role == Role.SYSTEM
    assert len(msgs[0].content.split()) == 1


def test_replace_replaces_messages() -> None:
    """replace 应整体替换消息，用于恢复已保存会话。"""
    ctx = Context()
    ctx.add(_make_msg(Role.USER, "old"))

    ctx.replace([_make_msg(Role.USER, "new")])
    msgs = ctx.messages()

    assert len(msgs) == 1
    assert msgs[0].content == "new"
