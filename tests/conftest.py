"""Pytest configuration, fixtures, and plugins."""

from __future__ import annotations

from pathlib import Path

import pytest

TEST_DIR = Path(__file__).parent


@pytest.fixture(scope="session")
def test_fixture_dir() -> Path:
    """Return path to the ``tests/fixtures/`` directory."""
    return TEST_DIR / "fixtures"


@pytest.fixture(scope="session")
def root_dir() -> Path:
    """Return path to the root directory."""
    return TEST_DIR.parent
