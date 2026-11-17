# manim-mcp Session Handoff
**Date:** 2026-02-24
**Status:** Complete — ready to use

---

## What Was Built

A production-grade MCP server that lets Claude render Manim animations directly from a conversation. You describe an animation → Claude writes Manim Python → the server executes it → MP4 + PNG preview come back.

---

## Repository Layout

```
manimV2/
├── CLAUDE.md                    ← project context (loaded every session)
├── SESSION_HANDOFF.md           ← this file
├── pyproject.toml               ← v2.0 package config (uvx-installable)
├── .mcp.json                    ← wires server into Claude Code (auto-loaded)
├── .venv/                       ← Python 3.11 venv: manim 0.20.0 + mcp
│
├── src/manim_mcp/               ← v2.0 ACTIVE implementation
│   ├── __init__.py
│   └── server.py                ← THE file (7 tools, DiagnosticsEngine)
│
└── manim_src/                   ← v0.2 REFERENCE (original 5-tool server)
    ├── server.py
    ├── PRD.md                   ← v2.0 spec (fully implemented)
    ├── pyproject.toml
    ├── README.md
    └── test_server.py
```

---

## To Use (after next session start)

Claude Code will auto-connect to the MCP server via `.mcp.json`. Just ask:

```
"Render a sine wave animation using Manim"
"Animate the Pythagorean theorem"
"Create a 3Blue1Brown-style calculus visualization"
```

Claude will call `validate_manim_code` → `suggest_quality` → `render_manim` automatically.

**Renders land at:** `~/.manim-mcp/renders/`

---

## 7 MCP Tools (all live, verified)

| Tool | Description |
|---|---|
| `render_manim` | Render one scene → MP4 + PNG preview + structured diagnostics |
| `render_manim_batch` | Render N scenes in parallel (asyncio Semaphore, cap=4) |
| `validate_manim_code` | Static analysis <100ms — catches errors before slow render |
| `suggest_quality` | Complexity score → quality recommendation + time estimates |
| `list_renders` | List cached renders, optional `filter_scene` param |
| `get_render_info` | Metadata + base64 MP4/PNG for a specific render_id |
| `cleanup_renders` | Delete old renders + sidecars, keep latest N |

---

## v2.0 Additions Over v0.2

- **DiagnosticsEngine** — 10 error codes (LATEX_NOT_FOUND, IMPORT_ERROR, NAME_ERROR, EMPTY_PLAY, RENDER_TIMEOUT, CAIRO_ERROR, etc.) parsed from raw Manim stderr
- **Preview frames** — FFmpeg extracts last frame as PNG after every render (base64 in response)
- **Sidecar files** — `{id}.json` metadata written atomically alongside every `.mp4`
- **render_manim_batch** — one call renders multiple scenes concurrently
- **suggest_quality** — complexity heuristic (play calls, MathTex count, ThreeDScene, ValueTracker, line count) → 1-10 score → recommended quality + time estimates
- **Extended validator** — deprecated API detection (ShowCreation→Create, etc.), ghost object heuristic, self.wait(0) no-op warning, ThreeDScene renderer suggestion
- **Security** — scene_name validated as Python identifier before subprocess interpolation
- **list_renders `filter_scene`** + sidecar metadata in response
- **cleanup_renders** deletes `.png` + `.json` sidecars too

---

## Environment

```
Python:   3.11 (.venv/bin/python)
Manim:    0.20.0 (.venv/bin/manim)
ffmpeg:   /opt/homebrew/bin/ffmpeg  ✓
uv:       ✓
LaTeX:    NOT installed (MathTex will fail — install: brew install --cask mactex)
```

---

## Plugins Installed This Session (6 new)

All registered in `~/.claude/plugins/installed_plugins.json`:
- `pyright-lsp` — Python type checking + code intelligence
- `skill-creator` — build/eval custom skills
- `claude-md-management` — CLAUDE.md audit + session learning capture
- `code-review` — multi-agent parallel PR review
- `feature-dev` — 7-phase structured feature development
- `commit-commands` — git commit workflow helpers

**Note:** Plugins active after Claude Code restart. Were manually installed (can't run `claude plugins install` inside a live session).

---

## What's Left / Next Steps

1. **LaTeX** — `brew install --cask mactex` (~3 GB) unlocks MathTex/Tex objects
2. **Tests** — update `manim_src/test_server.py` to cover v2.0 tools (DiagnosticsEngine, batch, suggest_quality)
3. **Publish** — push to GitHub → users can install via `uvx --from git+... manim-mcp`
4. **HTTP/SSE transport** — gate behind `MANIM_TRANSPORT=sse` for remote/Docker deployments
5. **Scene library** — catalog of reusable Manim templates Claude can compose from

---

## How Plugin Install Works (for future reference)

`claude plugins install <name>` cannot run inside a live Claude Code session (nested session error).

**Manual install steps:**
```bash
# 1. Copy from marketplace to cache
cp -r ~/.claude/plugins/marketplaces/claude-plugins-official/plugins/<name>/ \
      ~/.claude/plugins/cache/claude-plugins-official/<name>/<sha>/

# 2. Add entry to installed_plugins.json
# (see MEMORY.md for the exact JSON structure)

# 3. Restart Claude Code
```
