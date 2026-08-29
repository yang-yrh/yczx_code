"""计算器工具：只读、无副作用，用于演示工具调用链路。"""

from __future__ import annotations

import ast
import operator
from typing import Any

from .base import Tool, ToolError

_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY_OPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _eval_node(node: ast.AST) -> object:
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool):
            raise ToolError("表达式不支持布尔值")
        return node.value
    if isinstance(node, ast.BinOp):
        op = _BIN_OPS.get(type(node.op))
        if op is None:
            raise ToolError(f"不支持的运算符: {type(node.op).__name__}")
        return op(_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp):
        op = _UNARY_OPS.get(type(node.op))
        if op is None:
            raise ToolError(f"不支持的运算符: {type(node.op).__name__}")
        return op(_eval_node(node.operand))
    raise ToolError(f"不允许的表达式节点: {type(node).__name__}")


class CalculatorTool(Tool):
    """在 AST 白名单内安全计算算术表达式。"""

    name = "calculator"
    description = "安全地计算算术表达式，支持 + - * / // % ** 与括号。"
    parameters = {"expression": "string"}
    read_only = True
    concurrency_safe = True

    def __init__(self, workspace_root: Any = None) -> None:
        super().__init__(workspace_root)

    def run(self, arguments: dict[str, Any]) -> dict[str, Any]:
        expression = str(arguments.get("expression") or arguments.get("input") or "").strip()
        if not expression:
            raise ToolError("expression 不能为空")
        try:
            tree = ast.parse(expression, mode="eval")
            value = _eval_node(tree)
        except ToolError:
            raise
        except SyntaxError as exc:
            raise ToolError(f"表达式语非法: {exc}") from exc
        return {"expression": expression, "result": value}
