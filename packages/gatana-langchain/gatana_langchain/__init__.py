"""Gatana LangChain - A toolkit for building LangChain applications."""

from importlib.metadata import version

from .sandbox import GatanaSandbox

__version__: str = version("gatana-langchain")

__all__ = ["GatanaSandbox", "__version__"]
