"""应用配置与运行模式。"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path


class SandboxMode(StrEnum):
    """能力范围：能读、能写、能执行什么。"""

    READ_ONLY = "read-only"
    WORKSPACE_WRITE = "workspace-write"
    DANGER_FULL = "danger-full-access"


class ApprovalPolicy(StrEnum):
    """审批时机：什么时候向用户请求批准。"""

    ON_REQUEST = "on-request"
    AUTO = "auto"


@dataclass(frozen=True)
class ProviderConfig:
    """Provider 运行配置。"""

    name: str = "fake"
    base_url: str | None = None
    api_key_env: str | None = None
    model: str | None = None


@dataclass(frozen=True)
class AppConfig:
    """组合根使用的配置。"""

    workspace: Path
    provider: ProviderConfig = field(default_factory=ProviderConfig)
    max_steps: int = 8
    max_tokens: int = 8192
    timeout: int = 60
    sandbox_mode: SandboxMode = SandboxMode.READ_ONLY
    approval_policy: ApprovalPolicy = ApprovalPolicy.ON_REQUEST
    profile: str = "dev"
