"""插件注册表。"""

from __future__ import annotations

from typing import Any


class PluginRegistry:
    """插件注册与发现，与内置能力共用同一策略与审计路径。"""

    def __init__(self) -> None:
        self._plugins: dict[str, Any] = {}

    def register(self, plugin_id: str, entry: Any) -> None:
        self._plugins[plugin_id] = entry

    def get(self, plugin_id: str) -> Any:
        return self._plugins[plugin_id]
