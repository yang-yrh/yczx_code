"""记忆持久化端口与内存实现。"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..core.contracts import Message


class MemoryStore(ABC):
    """记忆存储端口。"""

    @abstractmethod
    def add(self, message: Message) -> None:
        """追加记忆。"""

    @abstractmethod
    def load(self) -> list[Message]:
        """读取全部记忆。"""


class InMemoryStore(MemoryStore):
    """进程内实现，测试与离线开发使用。"""

    def __init__(self) -> None:
        self._items: list[Message] = []

    def add(self, message: Message) -> None:
        self._items.append(message)

    def load(self) -> list[Message]:
        return list(self._items)
