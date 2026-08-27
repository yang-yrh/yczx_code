"""上下文：项目规则、消息裁剪与 token 预算。"""

from __future__ import annotations

from .contracts import Message


class Context:
    """维护会话消息与资源上限，不持有终端 UI。"""

    def __init__(self, max_tokens: int = 8192) -> None:
        self._max_tokens = max_tokens
        self._messages: list[Message] = []

    def add(self, message: Message) -> None:
        self._messages.append(message)

    def messages(self) -> list[Message]:
        """返回消息副本。"""
        return list(self._messages)

    def trim(self, budget_tokens: int | None = None) -> None:
        """按 token 预算裁剪消息。实现时按 tokenizer 估算。"""
        # TODO: 估算 token，超预算时压缩/裁剪。
        raise NotImplementedError

    def max_tokens(self) -> int:
        return self._max_tokens
