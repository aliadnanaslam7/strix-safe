"""Strix Safe guards around how local sources enter the sandbox."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from strix.config import load_settings
from strix.runtime.backends import backend_supports_bind_mounts


if TYPE_CHECKING:
    pass


def reject_writable_manifest_uploads_if_needed(
    backend_name: str,
    local_sources: list[dict[str, Any]],
) -> None:
    """Refuse local sources on non-bind-mount backends unless writable mounts allowed.

    Manifest backends upload ``LocalDir`` trees as writable copies inside the
    sandbox. Strix Safe blocks that path by default.
    """
    if backend_supports_bind_mounts(backend_name):
        return
    if not local_sources:
        return
    if load_settings().hardening.writable_mounts:
        return
    raise RuntimeError(
        "Strix Safe: runtime backend "
        f"{backend_name!r} copies local sources into the sandbox as "
        "writable trees (no read-only bind mounts). Use the default "
        "Docker bind-mount backend, or set STRIX_WRITABLE_MOUNTS=1 to "
        "allow writable uploads."
    )
