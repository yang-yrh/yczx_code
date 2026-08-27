"""会话状态、持久化、恢复与分叉。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from .contracts import Message


@dataclass
class Session:
    """一次对话的会话状态。"""

    session_id: str
    messages: list[Message] = field(default_factory=list)
    parent_id: str | None = None


class SessionStore(ABC):
    """会话持久化端口。"""

    @abstractmethod
    def load(self, session_id: str) -> Session:
        """读取会话。"""

    @abstractmethod
    def save(self, session: Session) -> None:
        """保存会话。"""

    @abstractmethod
    def fork(self, session: Session) -> Session:
        """从既有会话分叉出新分支。"""
