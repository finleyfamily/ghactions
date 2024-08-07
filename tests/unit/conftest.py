"""Pytest configuration, fixtures, and plugins."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

ENV_OVERRIDE: dict[str, str] = {
    "GITHUB_ACTION": "test-action",
    "GITHUB_ACTION_REF": "master",
    "GITHUB_ACTOR": "user",
    "GITHUB_EVENT_NAME": "push",
    "GITHUB_JOB": "test",
    "GITHUB_REF": "refs/pull/0/merge",
    "GITHUB_REF_NAME": "0/merge",
    "GITHUB_REF_PROTECTED": "false",
    "GITHUB_REPOSITORY": "finleyfamily/ghactions",
    "GITHUB_SHA": "abc123",
    "GITHUB_TOKEN": "gh_token",
    "GITHUB_TRIGGERING_ACTOR": "trigger-user",
    "GITHUB_WORKFLOW": "test-workflow",
    "GITHUB_WORKFLOW_REF": "master",
    "GITHUB_WORKFLOW_SHA": "abc123",
}
"""Environment variables that will be overridden with the value defined here."""

ENV_REMOVE = (
    "GITHUB_ACTION_REPOSITORY",
    "GITHUB_BASE_REF",
    "GITHUB_EVENT_PATH",
    "GITHUB_HEAD_REF",
    "GITHUB_WORKSPACE",
)
"""Environment variables that will be removed if present."""


@pytest.fixture(autouse=True, scope="session")
def environ(session_mocker: MockerFixture) -> dict[str, str]:
    """Patch ``os.environ``."""
    values = os.environ.copy()
    values.update(ENV_OVERRIDE)
    return session_mocker.patch.dict(os.environ, values, clear=True)
