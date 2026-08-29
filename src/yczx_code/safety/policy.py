"""工具策略：允许、拒绝或需要用户确认。"""

from __future__ import annotations

from ..core.contracts import PolicyDecision


class ToolPolicy:
    """统一工具策略入口，结合安全决策与用户确认偏好。"""

    def evaluate(
        self,
        tool_name: str,
        arguments: dict[str, object],
        read_only: bool = False,
    ) -> PolicyDecision:
        # Preview：只读工具放行，非只读默认拒绝。
        # 完整判定（sandbox_mode × approval_policy × 敏感操作）在后续实现。
        if read_only:
            return PolicyDecision.ALLOW
        return PolicyDecision.REJECT
