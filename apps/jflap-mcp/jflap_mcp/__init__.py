"""JFLAP MCP - Servidor MCP file-based para JFLAP 7.1."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version as _dist_version

try:
    __version__ = _dist_version("jflap-mcp")
except PackageNotFoundError:  # pragma: no cover - corriendo sin instalar
    __version__ = "0.0.0+source"

__all__ = ["__version__"]
