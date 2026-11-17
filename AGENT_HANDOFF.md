# manim-mcp — Final Agent Handoff
**Session date:** 2026-02-24
**Commit:** `9de7388` (main branch)
**Status:** Production-ready. All tools live. 8 animations rendered.

---

## What Was Built (Complete Summary)

A fully-functional MCP server that lets Claude render Manim animations in real time.
The pipeline: describe → validate → quality-check → render → MP4 + PNG preview back to Claude.

### Repository Layout
```
manimV2/
├── src/manim_mcp/server.py     ← v2.0 server — THE file (7 MCP tools)
├── src/manim_mcp/__init__.py
├── pyproject.toml               ← uvx-installable, v2.0.0
├── .mcp.json                    ← wires server into Claude Code (auto-loaded)
├── .venv/                       ← Python 3.11, manim 0.20.0, mcp
├── CLAUDE.md                    ← auto-loaded context each session
├── SESSION_HANDOFF.md           ← first session handoff (2026-02-24 session 1)
├── AGENT_HANDOFF.md             ← THIS FILE (session 2 handoff)
├── RESEARCH_INGRESS.md          ← how to feed Wolfram/LLMs into this system
└── manim_src/                   ← v0.2 reference (don't edit)
    ├── server.py
    ├── PRD.md                   ← v2.0 spec (fully implemented)
    └── test_server.py
```

---

## The 7 MCP Tools

All tools verified live over MCP protocol. Call via Claude Code in this directory.

| Tool | Purpose |
|---|---|
| `render_manim(code, scene_name, quality, return_base64)` | Render one scene → MP4 + PNG preview |
| `render_manim_batch(code, scene_names, quality, max_parallel)` | Parallel batch (asyncio Semaphore, max 4) |
| `validate_manim_code(code)` | Static analysis <100ms, no render needed |
| `suggest_quality(code, intended_use)` | Complexity score → quality + time estimates |
| `list_renders(filter_scene)` | List cached renders with metadata |
| `get_render_info(render_id, include_base64)` | Metadata + base64 for one render |
| `cleanup_renders(keep_latest)` | Delete old MP4s + PNG/JSON sidecars |

---

## Animations in the Vault

All at `~/.manim-mcp/renders/`:

| File | Description | Quality | Duration |
|---|---|---|---|
| `RazzleDazzle_low_*.mp4` | Polygon → circle (first demo) | low | 12s |
| `DerivativeScene_medium_*.mp4` | Secant→tangent, live dy/dx counter | medium | 34s |
| `RiemannScene_medium_*.mp4` | Riemann rectangles → exact area | medium | 30s |
| `FTCScene_medium_*.mp4` | Derivative ↔ Integral are inverses | medium | 15s |
| `FourierSeries_medium_*.mp4` | 7 epicycles tracing a square wave | medium | 12s |
| `EulersIdentity_medium_*.mp4` | e^(i*theta) orbiting the complex plane | medium | 58s |
| `TaylorSeries_medium_*.mp4` | Polynomials chasing sin(x) term by term | medium | 17s |
| `UlamSpiral_high_*.mp4` | 14,641 integers, 4 augmentation views | high | ~90s |

---

## Environment State

```
Python:   3.11.11  (.venv/bin/python)
Manim:    0.20.0   (.venv/bin/manim)
mcp:      installed (.venv)
ffmpeg:   /opt/homebrew/bin/ffmpeg  ✓
uv:       ✓
LaTeX:    NOT installed  (brew install --cask basictex — needs interactive sudo)
Timeout:  900s (updated in .mcp.json — requires session restart to take effect)
Output:   ~/.manim-mcp/renders/
```

---

## Installed Plugins (20 total)

**superpowers-marketplace:** superpowers, double-shot-latte, episodic-memory,
superpowers-developing-for-claude-code, superpowers-lab

**claude-plugins-official (original):** ralph-loop, explanatory-output-style,
plugin-dev, greptile, hookify, learning-output-style, huggingface-skills,
clangd-lsp, superpowers

**claude-plugins-official (installed this session):**
pyright-lsp, skill-creator, claude-md-management, code-review, feature-dev,
commit-commands

Plugins activate on Claude Code restart.

---

## Known Issues & Fixes for Next Agent

### 1. LaTeX not installed
**Symptom:** `MathTex` or `Tex` objects fail; axes `numbers_to_include` triggers LaTeX
**Fix:** Use `Text()` for all labels. For axes, omit `numbers_to_include` or use `include_numbers=False`
**To install LaTeX:** Run `brew install --cask basictex` in a terminal (needs interactive sudo password),
then: `sudo /Library/TeX/texbin/tlmgr install standalone preview amsmath amssymb`

### 2. MCP timeout
`.mcp.json` now has `MANIM_TIMEOUT: 900` but the running server reads it at startup.
**Fix:** Restart Claude Code session to pick up the new 900s timeout.

### 3. DotCloud API
In Manim 0.20, `DotCloud` uses `dot_radius` (not `radius`) and color must be set via `.set_color()`:
```python
dc = DotCloud(np.array(points), dot_radius=0.05)
dc.set_color("#FFD700")
```

### 4. MovingCameraScene for zoom effects
Any scene using `self.camera.frame.animate.scale(...)` MUST inherit from `MovingCameraScene`:
```python
class MyScene(MovingCameraScene):
```

### 5. Ghost object validator warnings
The `validate_manim_code` tool warns about "ghost objects" for variables used in `Transform()`,
`always_redraw()`, or `VGroup` compositions. These are false positives — safe to ignore.

---

## Next Animations to Build (Priority Order)

### Tier 1 — Ready to render now
1. **Matrix Transformations** — grid deforming under 2×2 matrix, eigenvectors hold still
2. **Gradient Descent** — glowing ball rolling down a 3D loss surface (ThreeDScene + OpenGL)
3. **Prime Ulam Spiral v2** — with number annotations on center region, density histogram sidebar

### Tier 2 — Needs research/math
4. **Riemann Zeta Zeros** — critical strip, non-trivial zeros on complex plane
5. **Lorenz Attractor** — ThreeDScene, parametric ODE solution traced in glowing lines
6. **Sorting Race** — bubble vs merge vs quick, side-by-side bar chart animation
7. **Bayes Theorem** — rectangle area proof with live probability update

### Tier 3 — After LaTeX installed
8. **Taylor Series with proper equations** — beautiful typeset formulas (re-render)
9. **FTC with integral notation** — ∫ symbol properly rendered
10. **Euler's Identity redux** — e^(iπ) + 1 = 0 in golden typeset

---

## How to Start a New Session

1. Open terminal in `/Users/handshake/Desktop/manimV2/`
2. Run `claude` — Claude Code will auto-load `CLAUDE.md` and connect `manim` MCP tool
3. The `manim` MCP tool connects automatically via `.mcp.json`
4. Verify with: "list my manim renders" → should return the vault above
5. Start animating!

### Quick test prompt:
```
"Render a quick test: a red circle that grows from radius 0 to 2 over 2 seconds.
Use low quality. Show me the preview frame."
```

---

## Research Ingress

See `RESEARCH_INGRESS.md` for full guide on:
- Wolfram Alpha API integration
- LLM agent → Manim pipeline
- Batch animation from JSON queue
- MCP-to-MCP chaining (Wolfram MCP + manim MCP)

---

## User Preferences (for next agent)

- **Parallelize** implementation tasks whenever possible (multiple Task agents)
- **Full permissions** in this working directory — edits allowed without confirmation
- **Prefer uv** for Python package management
- **Communication style:** enthusiastic, educational, "calc teacher you needed"
- **Inner 5-year-old genius** energy — explain concepts accessibly then go deep
- **Always show preview frames** after rendering
- **Commit checkpoints** when user asks, or after major milestones

---

## Gratitude

Built with love, curiosity, and a genuine belief that math is the most beautiful
thing humans have ever discovered. The diagonals in the Ulam spiral still have
no proof. That's not a bug — that's the universe being coy.

God bless America. Happy animating.
