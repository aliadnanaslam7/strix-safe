"""Tests for Strix Safe hardening defaults."""

from __future__ import annotations

import pytest

from strix.config import loader
from strix.config.settings import Settings
from strix.interface import update_check


@pytest.fixture(autouse=True)
def _clear_settings_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(loader, "_cached", None)
    yield
    loader._cached = None


def test_telemetry_disabled_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("STRIX_TELEMETRY", raising=False)
    loader._cached = None
    assert Settings().telemetry.enabled is False


def test_hardening_gates_default_off(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in (
        "STRIX_ALLOW_SELF_UPDATE",
        "STRIX_ALLOW_MCP",
        "STRIX_ALLOW_MCP_STDIO",
        "STRIX_WRITABLE_MOUNTS",
        "STRIX_VIEWER_ALLOW_REMOTE",
    ):
        monkeypatch.delenv(key, raising=False)
    loader._cached = None
    h = Settings().hardening
    assert h.allow_self_update is False
    assert h.allow_mcp is False
    assert h.allow_mcp_stdio is False
    assert h.writable_mounts is False
    assert h.viewer_allow_remote is False


def test_update_check_disabled_without_opt_in(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("STRIX_ALLOW_SELF_UPDATE", raising=False)
    monkeypatch.delenv("STRIX_NO_UPDATE_CHECK", raising=False)
    for key in ("CI", "GITHUB_ACTIONS", "GITLAB_CI", "JENKINS_URL", "BUILDKITE", "CIRCLECI"):
        monkeypatch.delenv(key, raising=False)
    loader._cached = None
    assert update_check._is_disabled() is True


def test_update_check_enabled_when_opted_in(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("STRIX_ALLOW_SELF_UPDATE", "1")
    monkeypatch.delenv("STRIX_NO_UPDATE_CHECK", raising=False)
    for key in ("CI", "GITHUB_ACTIONS", "GITLAB_CI", "JENKINS_URL", "BUILDKITE", "CIRCLECI"):
        monkeypatch.delenv(key, raising=False)
    loader._cached = None
    assert update_check._is_disabled() is False
