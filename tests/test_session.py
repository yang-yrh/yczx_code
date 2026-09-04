"""会话文件存储测试：保存、读取与分叉。"""

from __future__ import annotations

from pathlib import Path

from yczx_code.core.contracts import Message, Role
from yczx_code.core.session import FileSessionStore, Session


def test_file_session_save_load(tmp_path: Path) -> None:
    """保存后能按同一会话 ID 读取消息。"""
    store = FileSessionStore(tmp_path)

    session = Session(
        session_id="s1",
        messages=[Message(Role.SYSTEM, "hi")],
    )

    store.save(session)
    loaded = store.load("s1")

    assert loaded.session_id == "s1"
    assert len(loaded.messages) == 1
    assert loaded.messages[0].content == "hi"


def test_file_session_store_fork(tmp_path: Path) -> None:
    """分叉出的新会话应记录原会话为父会话，并保存到文件。"""
    store = FileSessionStore(tmp_path)

    session = Session(
        session_id="s1",
        messages=[Message(Role.SYSTEM, "hi")],
    )

    store.save(session)
    forked = store.fork(session)

    assert forked.parent_id == "s1"
    assert forked.session_id != "s1"
    assert forked.messages == session.messages

    loaded = store.load(forked.session_id)
    assert loaded.session_id == forked.session_id
    assert loaded.messages == forked.messages
