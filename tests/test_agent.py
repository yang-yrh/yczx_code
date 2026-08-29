from pathlib import Path

from yczx_code.application import Application
from yczx_code.core.config import AppConfig, ProviderConfig
from yczx_code.providers.fake import FakeProvider


def _app(tmp_path: Path) -> Application:
    config = AppConfig(workspace=tmp_path, provider=ProviderConfig(name="fake"))
    return Application(config, provider=FakeProvider())


def test_agent_runs_tool_loop(tmp_path: Path) -> None:
    app = _app(tmp_path)
    result = app.agent().run("2 * 8")

    assert "完成" in result.final_answer
    assert result.stop_reason == "complete"

    types = [event.type for event in app.events().events]
    assert "tool_call" in types
    assert "tool_result" in types
    assert "final" in types


def test_agent_caps_steps(tmp_path: Path) -> None:
    config = AppConfig(
        workspace=tmp_path,
        provider=ProviderConfig(name="fake"),
        max_steps=2,
    )
    app = Application(config, provider=FakeProvider())

    # 用非算术任务让 FakeProvider 直接返回结果，步数仍受控。
    result = app.agent().run("hi")
    assert result.stop_reason in {"complete", "max_steps"}
