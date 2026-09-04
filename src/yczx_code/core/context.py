"""上下文：项目规则、消息裁剪与 token 预算。"""

from __future__ import annotations

from .contracts import Message, Role


class Context:
    """维护会话消息与资源上限，不持有终端 UI。"""

    def __init__(self, max_tokens: int = 8192) -> None:
        self._max_tokens = max_tokens
        self._messages: list[Message] = []

    def add(self, message: Message) -> None:
        self._messages.append(message)

    def replace(self, messages: list[Message]) -> None:
        """整体替换消息列表，用于恢复已保存的会话。"""
        self._messages = list(messages)

    def messages(self) -> list[Message]:
        """返回消息副本。"""
        return list(self._messages)

    def trim(self, budget_tokens: int | None = None) -> None:
        """按 token 预算裁剪消息，优先保留系统消息与最近的对话内容。"""
        budget = self._max_tokens if budget_tokens is None else budget_tokens
        if budget <= 0:
            self._messages = []
            return

        retained: list[Message] = []
        remaining = budget

        # 系统消息优先保留；只有预算不足时才截断其内容。
        for message in self._messages:
            if message.role is not Role.SYSTEM:
                continue
            tokens = self._estimate_tokens(message.content)
            if tokens <= remaining:
                retained.append(message)
                remaining -= tokens
            else:
                words = message.content.split()
                if remaining > 0:
                    retained.append(Message(role=Role.SYSTEM, content=" ".join(words[:remaining])))
                remaining = 0
        # 从最新消息往前保留，放不下时再丢弃更早的非系统消息。
        recent: list[Message] = []
        for message in reversed(self._messages):
            if message.role is Role.SYSTEM:
                continue
            tokens = self._estimate_tokens(message.content)
            if tokens > remaining:
                break
            recent.append(message)
            remaining -= tokens
        retained.extend(reversed(recent))
        self._messages = retained

    def max_tokens(self) -> int:
        return self._max_tokens

    @staticmethod
    def _estimate_tokens(content: str) -> int:
        """先用空格分词估算 token，接入真实 tokenizer 后再替换。"""
        return max(1, len(content.split()))
