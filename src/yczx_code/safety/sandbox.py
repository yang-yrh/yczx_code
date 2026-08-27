"""沙箱边界：工作区隔离、敏感文件拒绝与资源限制。"""

from __future__ import annotations

from pathlib import Path

SENSITIVE_PARTS = frozenset(
    {".env", ".git", ".ssh", ".aws", ".config", ".cache", ".npmrc", ".gitconfig"}
)


def resolve_workspace(root: Path) -> Path:
    """解析并归一化工作区根目录。"""
    return root.resolve()


def is_outside(root: Path, target: Path) -> bool:
    """target 是否位于 root 之外。"""
    resolved_root = root.resolve()
    resolved_target = target.resolve()
    return resolved_root not in resolved_target.parents and resolved_target != resolved_root


def is_sensitive(target: Path) -> bool:
    """target 是否命中敏感目录或文件。"""
    return any(part in SENSITIVE_PARTS for part in target.parts)


def enforce_limits(*, max_steps: int, max_tokens: int, timeout: int) -> None:
    """资源上限检查，越界时抛出异常。"""
    # TODO: 步数、token、字节、目录项、搜索结果与超时。
    raise NotImplementedError
