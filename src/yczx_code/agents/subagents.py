"""子 Agent 编排：Spawn 与 Fork。"""

from __future__ import annotations

from ..core.session import Session, SessionStore


class SubagentManager:
    """父 Agent 派生子 Agent 的编排入口。"""

    def __init__(self, store: SessionStore) -> None:
        self._store = store

    def spawn(self, task: str, session: Session) -> Session:
        """以全新上下文生成子 Agent。"""
        # TODO: 为新任务创建独立上下文。
        raise NotImplementedError

    def fork(self, session: Session, prompt: str) -> Session:
        """从既有会话分叉出新分支。"""
        return self._store.fork(session)
