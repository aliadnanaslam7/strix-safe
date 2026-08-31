# Strix Safe — Team Hardening Guide

This repository is a **public hardened fork** of [usestrix/strix](https://github.com/usestrix/strix):

**https://github.com/aliadnanaslam7/strix-safe**

Safe defaults are baked into the code. Teammates should install from **this fork**, not from `curl https://strix.ai/install | bash`.

## Install

```bash
git clone git@github.com:aliadnanaslam7/strix-safe.git
cd strix-safe
uv sync   # or: pip install -e .
```

Keep an `upstream` remote for periodic merges:

```bash
git remote add upstream git@github.com:usestrix/strix.git
git fetch upstream
```

## Safe defaults (no env required)

| Control | Default | Opt-in |
|---|---|---|
| Telemetry (PostHog / Scarf) | **Off** | `STRIX_TELEMETRY=1` |
| Background self-update checks | **Off** | `STRIX_ALLOW_SELF_UPDATE=1` |
| MCP servers | **Off** | `STRIX_ALLOW_MCP=1` and/or `--mcp-config PATH` |
| MCP stdio (host subprocesses) | **Off** | `STRIX_ALLOW_MCP_STDIO=1` (also needs MCP allow) |
| Local target bind mounts | **Read-only** | `STRIX_WRITABLE_MOUNTS=1` |
| Viewer bind address | **Loopback only** | `STRIX_VIEWER_ALLOW_REMOTE=1` for non-`127.0.0.1` |
| Non-bind-mount backends + local sources | **Refused** (would upload writable copies) | Use Docker bind mounts, or `STRIX_WRITABLE_MOUNTS=1` |

`strix --update` and package-manager “upgrade strix-agent” paths are **disabled** for this fork — they would pull upstream `usestrix/strix` / PyPI and drop Safe defaults. Update with `git pull` on this repo instead.

## Recommended first scan

```bash
export STRIX_LLM="openai/gpt-5.4"   # or your provider
export LLM_API_KEY="..."

# Optional belt-and-suspenders (already the defaults):
export STRIX_TELEMETRY=0

# Prefer scanning a copy of the tree, not your only working copy
strix --target /path/to/copy-of-app
```

## When you need to relax a gate

```bash
# Allow agent to write into mounted source (autofix / apply_patch on host files)
export STRIX_WRITABLE_MOUNTS=1

# Enable MCP from a reviewed config (HTTP only unless stdio also allowed)
export STRIX_ALLOW_MCP=1
strix --target ./app --mcp-config ./reviewed-mcp-servers.json

# Allow stdio MCP (runs processes on the HOST — review carefully)
export STRIX_ALLOW_MCP=1
export STRIX_ALLOW_MCP_STDIO=1

# Bind viewer on all interfaces (share the tokened URL carefully)
export STRIX_VIEWER_ALLOW_REMOTE=1
strix view --host 0.0.0.0
```

## Do not

- Install via `curl -sSL https://strix.ai/install | bash` for team machines using this fork
- Run `strix --update` / `pip install --upgrade strix-agent` expecting Safe defaults to remain
- Point teammates at upstream PyPI/`strix-agent` if you need these defaults
- Enable MCP stdio against untrusted server configs
- Mount home directories or credential stores (the tool already refuses many of these)
- Rely on non-bind-mount runtime backends with local sources unless you intentionally set `STRIX_WRITABLE_MOUNTS=1`

## Tracking upstream

Review upstream changelogs before merging, especially for:

- `strix/tools/mcp/`
- `strix/runtime/session_manager.py` (mounts)
- `strix/telemetry/`
- `strix/interface/update_check.py`
- `strix/interface/viewer/`
