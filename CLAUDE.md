# manim-mcp — Claude Code Project Context

## What This Is
A production-grade MCP server that lets Claude write and render Manim animations.
Claude calls `render_manim` → server executes Manim → MP4 comes back (optionally with a
base64 preview frame). The full loop: describe → write code → render → observe → iterate.

## Key Files
```
manim_src/           # Original v0.2 server (reference / backup)
  server.py          # Original 5-tool FastMCP server
  PRD.md             # v2.0 specification (authoritative)
  pyproject.toml     # Package config (uvx-installable)
  test_server.py     # Unit tests (no manim install required)

src/manim_mcp/       # v2.0 implementation (active)
  __init__.py
  server.py          # v2.0 FastMCP server — THE file to edit

.venv/               # uv venv with manim 0.20.0 + mcp installed
.mcp.json            # Project MCP config — wires this server into Claude Code
```

## Runtime
- Python: `.venv/bin/python` (3.11, manim 0.20.0, mcp)
- Manim binary: `.venv/bin/manim`
- Render output: `~/.manim-mcp/renders/`
- MCP transport: stdio (project .mcp.json active)

## v2.0 Features (implemented in src/manim_mcp/server.py)
- `DiagnosticsEngine` — parses raw Manim stderr into structured error objects
- `render_manim` — adds `preview_frame` (PNG) + `diagnostics` + scene name validation
- `render_manim_batch` — parallel batch rendering with asyncio Semaphore
- `suggest_quality` — complexity heuristic → recommended quality + estimated seconds
- `validate_manim_code` — extended: deprecated APIs, ghost objects, ThreeDScene hint
- `list_renders(filter_scene=)` — optional filter
- `get_render_info` — returns PNG preview sidecar
- `cleanup_renders` — also deletes .png and .json sidecars

## Sidecar Files
Each render produces up to 3 files in `MANIM_OUTPUT_DIR`:
- `{render_id}.mp4` — the video
- `{render_id}.png` — final-frame preview (extracted by FFmpeg)
- `{render_id}.json` — metadata (scene_name, quality, rendered_at, duration, code_sha256)

## Dev Commands
```bash
# Run tests (no manim needed)
.venv/bin/pytest manim_src/test_server.py -v

# Test server directly
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | \
  .venv/bin/python src/manim_mcp/server.py

# Quick render smoke test
.venv/bin/manim --version
```

## System Dependencies (macOS)
- cairo, pango, ffmpeg: installed via homebrew
- LaTeX: NOT currently installed (MathTex will fail without mactex)
- Install LaTeX: `brew install --cask mactex` (3 GB, slow)

## MCP Config (.mcp.json)
Points Claude Code at `src/manim_mcp/server.py` using the local venv Python.
Restart Claude Code session to pick up after any server.py changes.

## Package Structure Note
`pyproject.toml` uses `src/` layout with `[project.scripts] manim-mcp = "manim_mcp.server:main"`.
For uvx install: `uvx --from git+https://github.com/YOUR_ORG/manim-mcp.git manim-mcp`

## Quality Presets
| Level | Resolution | FPS | Use Case |
|---|---|---|---|
| low | 480p | 15 | Fast iteration |
| medium | 720p | 30 | Review |
| high | 1080p | 60 | Near-final |
| production | 2160p | 60 | Final output |
