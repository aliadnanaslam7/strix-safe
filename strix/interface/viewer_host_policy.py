"""Viewer bind-address policy (Strix Safe).

Kept outside ``strix.interface.viewer`` so unit tests can load it without the
``agents`` SDK / TUI import graph.
"""

from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from rich.console import Console


def is_loopback_host(host: str) -> bool:
    normalized = host.strip().lower().strip("[]")
    return normalized in {"127.0.0.1", "localhost", "::1"}


def reject_remote_host_unless_allowed(host: str, console: Console) -> None:
    """Block non-loopback binds unless ``STRIX_VIEWER_ALLOW_REMOTE=1``."""
    from strix.config import load_settings

    if is_loopback_host(host):
        return
    if load_settings().hardening.viewer_allow_remote:
        return
    console.print(
        f"[bold red]Refusing to bind viewer to '{host}'.[/]\n"
        "Strix Safe defaults to loopback only. Use [cyan]--host 127.0.0.1[/] "
        "(default), or set [cyan]STRIX_VIEWER_ALLOW_REMOTE=1[/] to allow remote binds."
    )
    raise SystemExit(2)
