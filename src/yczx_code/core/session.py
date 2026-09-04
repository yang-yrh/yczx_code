"""会话状态、持久化、恢复与分叉。"""

from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from uuid import uuid4

from .contracts import Message, Role


@dataclass
class Session:
    """一次对话的会话状态。"""

    session_id: str
    messages: list[Message] = field(default_factory=list)
    parent_id: str | None = None


class SessionStoreError(Exception):
    """会话存储模块错误。"""


class SessionNotFoundError(SessionStoreError):
    """指定对话不存在。"""


class SessionStore(ABC):
    """会话持久化端口。"""

    @abstractmethod
    def save(self, session: Session) -> None:
        """保存会话。"""

    @abstractmethod
    def load(self, session_id: str) -> Session:
        """读取会话。"""

    @abstractmethod
    def fork(self, session: Session) -> Session:
        """从既有会话分叉出新分支。"""


class FileSessionStore(SessionStore):
    """基于本地 JSON 文件的会话存储。"""

    def __init__(self, root: Path) -> None:
        self._root = root

    def _path_for(self, session_id: str) -> Path:
        """把会话 ID 映射到根目录内的稳定文件名，避免路径穿越。"""
        digest = hashlib.sha256(session_id.encode("utf-8")).hexdigest()
        return self._root.resolve() / f"{digest}.json"

    def save(self, session: Session) -> None:
        """把会话写入 JSON 文件。"""

        payload = {
            "session_id": session.session_id,
            "parent_id": session.parent_id,
            "messages": [
                {"role": message.role.value, "content": message.content}
                for message in session.messages
            ],
        }
        path = self._path_for(session.session_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def load(self, session_id: str) -> Session:
        """读取并还原对话文件。"""
        path = self._path_for(session_id)
        if not path.exists():
            raise SessionNotFoundError(f"session not found: {session_id}")
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            messages = [
                Message(role=Role(message["role"]), content=message["content"])
                for message in payload.get("messages", [])
            ]
        except (KeyError, TypeError, ValueError) as exc:
            raise SessionStoreError(f"invalid session file: {session_id}") from exc
        return Session(
            session_id=str(payload["session_id"]),
            messages=messages,
            parent_id=payload.get("parent_id"),
        )

    def fork(self, session: Session) -> Session:
        """从既有会话创建新分支，并立即保存。"""
        forked = Session(
            session_id=uuid4().hex,
            messages=list(session.messages),
            parent_id=session.session_id,
        )
        self.save(forked)
        return forked
