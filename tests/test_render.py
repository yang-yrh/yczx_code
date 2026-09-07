from yczx_code.core.contracts import AgentEvent
from yczx_code.ui.render import TerminalRenderer


def test_render_final(capsys) -> None:
    """测试 final 事件"""
    renderer = TerminalRenderer()

    event = AgentEvent(
        event_id="event_1",
        type="final",
        payload={"content": "任务完成"},
    )

    renderer.render(event)

    captured = capsys.readouterr()

    assert "任务完成" in captured.out

def test_render_tool_call(capsys) -> None:
    """测试tool_call事件"""
    renderer = TerminalRenderer()

    event = AgentEvent(
        event_id="event_2",
        type="tool_call",
        payload={
            "call_id": "call_1",
            "name": "calculator",
            "arguments": {"expression": "1 + 2"},
        },
    )

    renderer.render(event)

    captured = capsys.readouterr()

    assert "调用工具 calculator" in captured.err
    assert "1 + 2" in captured.err

def test_render_tool_result(capsys) -> None:
    """测试tool_result事件"""
    renderer = TerminalRenderer()

    event = AgentEvent(
        event_id="event_3",
        type="tool_result",
        payload={
            "call_id": "call_1",
            "name": "calculator",
            "status": "ok",
            "summary": "expression=1 + 2 | result=3",
        },
    )

    renderer.render(event)

    captured = capsys.readouterr()

    assert "工具结果 calculator" in captured.err
    assert "result=3" in captured.err

def test_render_model_request(capsys) -> None:
    """测试model_request事件"""
    renderer = TerminalRenderer()

    event = AgentEvent(
        event_id="event_4",
        type="model_request",
        payload={
            "step": 1,
            "tool_names": ["calculator"],
        },
    )

    renderer.render(event)

    captured = capsys.readouterr()

    assert "[model] step=1" in captured.err
    assert "calculator" in captured.err

def test_render_unknown_event_does_not_crash(capsys) -> None:
    """测试未知事件类型不会导致render崩溃"""
    renderer = TerminalRenderer()

    event = AgentEvent(
        event_id="event_5",
        type="unknown_event",
        payload={},
    )

    renderer.render(event)

    captured = capsys.readouterr()

    assert captured.out == ""
    assert captured.err == ""