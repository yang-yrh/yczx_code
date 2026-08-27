"""面向编码任务的 Agent。"""

from __future__ import annotations

from ..core.agent import Agent
from ..core.contracts import AgentResult


class CodingAgent(Agent):
    """在本地代码库中执行任务的 Agent，可调用只读与写工具。"""

    def run(self, task: str) -> AgentResult:
        # TODO: 观察-思考-行动循环，工具经 registry 与 policy，事件与预算受限。
        raise NotImplementedError
