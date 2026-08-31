"""Tests for Strix Safe hardening defaults."""

from __future__ import annotations

import json
from pathlib import Path

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


def test_persist_current_skips_ephemeral_hardening_flags(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cfg = tmp_path / "cli-config.json"
    monkeypatch.setattr(loader, "_override", cfg)
    monkeypatch.setenv("STRIX_LLM", "test/model")
    monkeypatch.setenv("STRIX_ALLOW_MCP", "1")
    monkeypatch.setenv("STRIX_ALLOW_MCP_STDIO", "1")
    monkeypatch.setenv("STRIX_WRITABLE_MOUNTS", "1")
    loader._cached = None

    loader.persist_current()

    data = json.loads(cfg.read_text(encoding="utf-8"))
    env = data["env"]
    assert env.get("STRIX_LLM") == "test/model"
    assert "STRIX_ALLOW_MCP" not in env
    assert "STRIX_ALLOW_MCP_STDIO" not in env
    assert "STRIX_WRITABLE_MOUNTS" not in env


def test_json_overrides_ignore_ephemeral_hardening_flags(tmp_path: Path) -> None:
    path = tmp_path / "cli-config.json"
    path.write_text(
        json.dumps(
            {
                "env": {
                    "STRIX_ALLOW_MCP": "1",
                    "STRIX_WRITABLE_MOUNTS": "1",
                    "STRIX_LLM": "from-file",
                }
            }
        ),
        encoding="utf-8",
    )
    nested = loader._read_json_overrides(path)
    assert "hardening" not in nested
    assert nested["llm"]["model"] == "from-file"


def test_invalidate_settings_cache_picks_up_new_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("STRIX_ALLOW_MCP", raising=False)
    loader.invalidate_settings_cache()
    assert loader.load_settings().hardening.allow_mcp is False
    monkeypatch.setenv("STRIX_ALLOW_MCP", "1")
    loader.invalidate_settings_cache()
    assert loader.load_settings().hardening.allow_mcp is True


def test_viewer_rejects_remote_host_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    import io

    from rich.console import Console

    from strix.interface.viewer_host_policy import (
        is_loopback_host,
        reject_remote_host_unless_allowed,
    )

    monkeypatch.delenv("STRIX_VIEWER_ALLOW_REMOTE", raising=False)
    loader._cached = None
    assert is_loopback_host("127.0.0.1")
    assert is_loopback_host("localhost")
    with pytest.raises(SystemExit) as exc:
        reject_remote_host_unless_allowed("0.0.0.0", Console(file=io.StringIO()))
    assert exc.value.code == 2


def test_viewer_allows_remote_when_opted_in(monkeypatch: pytest.MonkeyPatch) -> None:
    import io

    from rich.console import Console

    from strix.interface.viewer_host_policy import reject_remote_host_unless_allowed

    monkeypatch.setenv("STRIX_VIEWER_ALLOW_REMOTE", "1")
    loader._cached = None
    reject_remote_host_unless_allowed("0.0.0.0", Console(file=io.StringIO()))


def test_manifest_backend_refuses_local_sources_without_writable_opt_in(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from strix.runtime.safe_mounts import reject_writable_manifest_uploads_if_needed

    monkeypatch.delenv("STRIX_WRITABLE_MOUNTS", raising=False)
    loader._cached = None

    with pytest.raises(RuntimeError, match="writable"):
        reject_writable_manifest_uploads_if_needed(
            "modal",
            [
                {
                    "source_path": str(tmp_path),
                    "workspace_subdir": "repo",
                    "protect_metadata": False,
                }
            ],
        )

    monkeypatch.setenv("STRIX_WRITABLE_MOUNTS", "1")
    loader._cached = None
    reject_writable_manifest_uploads_if_needed(
        "modal",
        [{"source_path": str(tmp_path), "workspace_subdir": "repo", "protect_metadata": False}],
    )
