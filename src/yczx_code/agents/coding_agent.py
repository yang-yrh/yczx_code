"""面向编码任务的 Agent：实现有界 ReAct 循环。"""

from __future__ import annotations

from uuid import uuid4

from ..core.agent import Agent
from ..core.contracts import (
    AgentEvent,
    AgentResult,
    Message,
    PolicyDecision,
    ProviderResponse,
    Role,
    ToolCall,
    ToolResult,
    ToolResultStatus,
    ToolSpec,
)

_SYSTEM_PROMPT = (
    "你是一个终端 Coding Agent。在需要时可调用工具获取结果，并用中文给出简洁、准确的最终回答。"
)


class CodingAgent(Agent):
    """在本地代码库中执行任务的 Agent，经工具注册表与统一策略调用工具。"""

    def run(self, task: str) -> AgentResult:
        """执行一次任务：模型→工具→回填，直至无工具调用或达到步数上限。"""
        self._context.add(Message(Role.SYSTEM, _SYSTEM_PROMPT))
        self._context.add(Message(Role.USER, task))
        specs = self._tool_specs()

        final_answer = ""
        step = 0
        while step < self._config.max_steps:
            step += 1
            self._context.trim()
            self._emit("model_request", {"step": step, "tool_names": [s.name for s in specs]})
            response = self._provider.chat(self._context.messages(), specs)
            if response.tool_calls:
                self._apply_tool_calls(response)
                continue
            final_answer = response.content
            self._emit("final", {"content": final_answer})
            return AgentResult(
                stop_reason="complete",
                final_answer=final_answer,
                usage={"steps": step},
            )

        message = final_answer or "已达到最大步数，任务未完成。"
        self._emit("final", {"content": message, "stop_reason": "max_steps"})
        return AgentResult(
            stop_reason="max_steps",
            final_answer=message,
            usage={"steps": step},
        )

    def _tool_specs(self) -> list[ToolSpec]:
        """由注册表生成模型可见的工具定义。"""
        return [
            ToolSpec(name=tool.name, description=tool.description, parameters=tool.parameters)
            for tool in self._tools.all()
        ]

    def _apply_tool_calls(self, response: ProviderResponse) -> None:
        """追加 assistant 消息，并逐个执行工具、回填结果。"""
        self._context.add(Message(Role.ASSISTANT, response.content))
        for call in response.tool_calls:
            self._emit(
                "tool_call",
                {"call_id": call.call_id, "name": call.name, "arguments": call.arguments},
            )
            result = self._execute_tool(call)
            self._emit(
                "tool_result",
                {
                    "call_id": call.call_id,
                    "name": call.name,
                    "status": result.status.value,
                    "summary": result.summary,
                },
            )
            self._context.add(Message(Role.TOOL, f"{result.status.value}: {result.summary}"))

    def _execute_tool(self, call: ToolCall) -> ToolResult:
        """执行单个工具，先经策略判定，再进入注册表分发。"""
        if call.name not in self._tools.names():
            return ToolResult(
                call_id=call.call_id,
                status=ToolResultStatus.ERROR,
                summary=f"未知工具 {call.name}",
                error="unknown_tool",
            )
        tool = self._tools.get(call.name)
        decision = self._policy.evaluate(call.name, call.arguments, tool.read_only)
        if decision is PolicyDecision.REJECT:
            return ToolResult(
                call_id=call.call_id,
                status=ToolResultStatus.ERROR,
                summary="策略拒绝执行",
                error="rejected",
            )
        try:
            data = tool.run(call.arguments)
            summary = self._summarize(data)
            return ToolResult(
                call_id=call.call_id,
                status=ToolResultStatus.OK,
                summary=summary,
                data=data,
            )
        except Exception as exc:
            return ToolResult(
                call_id=call.call_id,
                status=ToolResultStatus.ERROR,
                summary=str(exc),
                error=type(exc).__name__,
            )

    def _emit(self, event_type: str, payload: dict[str, object]) -> None:
        """向事件流追加一条事件。"""
        self._events.append(AgentEvent(event_id=uuid4().hex, type=event_type, payload=payload))

    @staticmethod
    def _summarize(data: object) -> str:
        """把结构化结果压缩为可读摘要。"""
        if isinstance(data, dict):
            return " | ".join(f"{key}={value}" for key, value in data.items())
        return str(data)
