"""Smoke tests for the gatana-langchain package."""

from __future__ import annotations

import gatana_langchain


def test_version_is_string() -> None:
    """Package exposes a version string."""
    assert isinstance(gatana_langchain.__version__, str)


def test_version_not_empty() -> None:
    """Version string is not empty."""
    assert len(gatana_langchain.__version__) > 0
