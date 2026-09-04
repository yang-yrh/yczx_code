"""Application 会话存储接线测试。"""

from __future__ import annotations

from pathlib import Path

from yczx_code.application import Application
from yczx_code.core.config import AppConfig, ProviderConfig
from yczx_code.core.session import FileSessionStore


def make_config(tmp_path: Path) -> AppConfig:
    """创建测试配置，使用 FakeProvider 离线运行。"""
    return AppConfig(
        workspace=tmp_path,
        provider=ProviderConfig(name="fake"),
    )


def test_application_exposes_injected_session_store(tmp_path: Path) -> None:
    """传入的会话存储应能从 Application 原样取回。"""
    store = FileSessionStore(tmp_path)
    app = Application(make_config(tmp_path), store=store)

    assert app.session_store() is store


def test_application_without_store_returns_none(tmp_path: Path) -> None:
    """未传入会话存储时，接口应返回 None。"""
    app = Application(make_config(tmp_path))

    assert app.session_store() is None


def test_application_run_saves_session(tmp_path: Path) -> None:
    """Application.run 应把本次上下文保存到会话存储。"""
    store = FileSessionStore(tmp_path)
    app = Application(make_config(tmp_path), store=store)

    app.run("hi", session_id="s1")
    session = store.load("s1")

    assert session.session_id == "s1"
    assert any(message.content == "hi" for message in session.messages)


def test_application_run_reuses_session(tmp_path: Path) -> None:
    """同一会话 ID 再次运行时应恢复并追加历史消息。"""
    store = FileSessionStore(tmp_path)
    app = Application(make_config(tmp_path), store=store)

    app.run("hi", session_id="s1")
    app.run("hello", session_id="s1")
    session = store.load("s1")

    assert session.session_id == "s1"
    assert any(message.content == "hi" for message in session.messages)
    assert any(message.content == "hello" for message in session.messages)
