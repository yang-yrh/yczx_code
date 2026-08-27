"""仅追加事件流：轨迹、回放与观测的统一底稿。"""

from __future__ import annotations

from dataclasses import dataclass, field

from .contracts import AgentEvent


@dataclass
class EventStream:
    """append-only 事件流，供日志、回放与评测使用。"""

    events: list[AgentEvent] = field(default_factory=list)

    def append(self, event: AgentEvent) -> None:
        self.events.append(event)

    def tail(self, count: int = 1) -> list[AgentEvent]:
        return self.events[-count:]
