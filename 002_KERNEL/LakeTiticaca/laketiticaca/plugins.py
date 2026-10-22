"""
plugins.py — Plugin/extension registry. Lets Interface (011) or third-party
modules register additional capabilities into the Kernel AI without it
needing to know about them at import time.
"""
from __future__ import annotations
from typing import Any, Dict, Protocol


class Plugin(Protocol):
    name: str

    def on_register(self) -> None: ...
    def on_unregister(self) -> None: ...


class PluginError(Exception):
    pass


class PluginRegistry:
    def __init__(self) -> None:
        self._plugins: Dict[str, Any] = {}

    def register(self, plugin: Any) -> None:
        name = getattr(plugin, "name", None)
        if not name:
            raise PluginError("plugin must have a 'name' attribute")
        if name in self._plugins:
            raise PluginError(f"plugin '{name}' already registered")
        self._plugins[name] = plugin
        if hasattr(plugin, "on_register"):
            plugin.on_register()

    def unregister(self, name: str) -> None:
        plugin = self._plugins.pop(name, None)
        if plugin is not None and hasattr(plugin, "on_unregister"):
            plugin.on_unregister()

    def get(self, name: str) -> Any:
        return self._plugins.get(name)

    def list_plugins(self) -> list[str]:
        return list(self._plugins.keys())
