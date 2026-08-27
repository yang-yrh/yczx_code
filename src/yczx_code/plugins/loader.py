"""插件清单与加载。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PluginManifest:
    """插件清单：身份、兼容性、能力、权限与网络访问。"""

    plugin_id: str
    version: str
    api_version: str
    entry: str
    capabilities: tuple[str, ...]
    permissions: tuple[str, ...]
    network: bool = False
    license: str = "proprietary"


class PluginLoader:
    """按清单加载插件，校验版本兼容与能力声明。"""

    def load(self, path: str) -> PluginManifest:
        # TODO: 读取清单、校验 API 版本与权限，拒绝不兼容插件。
        raise NotImplementedError

    def validate(self, manifest: PluginManifest) -> None:
        # TODO: 名称冲突、未知权限与不兼容版本直接拒绝。
        raise NotImplementedError
