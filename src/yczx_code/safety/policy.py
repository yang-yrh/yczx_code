"""工具策略：允许、拒绝或需要用户确认。"""

from __future__ import annotations

from ..core.contracts import PolicyDecision


class ToolPolicy:
    """统一工具策略入口，结合安全决策与用户确认偏好。"""

    def evaluate(self, tool_name: str, arguments: dict[str, object]) -> PolicyDecision:
        # TODO: 结合 sandbox_mode、approval_policy 与敏感操作判定。
        return PolicyDecision.REJECT
