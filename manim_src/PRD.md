# manim-mcp: Product Requirements Document
## Version 2.0 — For Agent Team Implementation

**Document status:** Draft  
**Audience:** Autonomous coding agents, multi-agent pipelines, and human engineers  
**Replaces:** Archived `Stelath/manim-mcp` repo; supersedes `abhiemj/manim-mcp-server`

---

## 1. Purpose and Problem Statement

Manim Community Edition is the leading Python library for programmatic mathematical animation. Connecting it to LLMs via the Model Context Protocol (MCP) creates a powerful loop: Claude (or any MCP client) can write Manim code, execute it, observe the error or success output, revise the code, and iterate until the animation is correct — all within a single conversation.

The two most-referenced open-source Manim MCP servers (`Stelath/manim-mcp` and `abhiemj/manim-mcp-server`) are either archived or under-engineered. The goal of this project is to produce a **production-grade, uvx-installable, well-tested MCP server** that any developer can drop into their Claude Code or Claude Desktop workflow with a single configuration line.

The reference implementation in this repository (`src/manim_mcp/server.py`) constitutes version 0.2. This PRD specifies **version 2.0**, which adds streaming render progress, a preview-image tool, multi-scene batch rendering, a quality-suggestion heuristic, and deeper error diagnostics. Agent teams should implement v2.0 against this spec.

---

## 2. Architecture Overview

### 2.1 System Context

```
┌─────────────────────────────────────────────┐
│              Claude Code / Claude Desktop    │
│  (MCP Client — sends tool calls over stdio) │
└───────────────────┬─────────────────────────┘
                    │ JSON-RPC over stdio
                    ▼
┌─────────────────────────────────────────────┐
│               manim-mcp server              │
│  (FastMCP — orchestrates tools & lifecycle) │
├─────────────────────────────────────────────┤
│  RenderEngine      │  CacheManager          │
│  (async subprocess)│  (content-addressed)   │
│                    │                        │
│  Validator         │  DiagnosticsEngine     │
│  (static analysis) │  (error interpretation)│
└───────────────────┬─────────────────────────┘
                    │ subprocess
                    ▼
┌─────────────────────────────────────────────┐
│           Manim Community Edition           │
│   (cairo, pango, ffmpeg, LaTeX — system)   │
└─────────────────────────────────────────────┘
```

### 2.2 Transport and Protocol

The server MUST use **stdio transport** as its primary mode. This is the only transport natively supported by Claude Code's MCP integration. The server MUST NOT write anything to stdout except well-formed JSON-RPC messages — any debug output, progress indicators, or logging MUST go to stderr.

An optional **HTTP/SSE transport** MAY be supported as a secondary mode for use with remote or Docker-hosted Manim rendering farms. If implemented, it must be gated by a `MANIM_TRANSPORT=sse` environment variable and must not affect the stdio path.

### 2.3 Packaging Requirements (Critical)

The server MUST be installable via `uvx` without cloning the repository. This requires:

- A `pyproject.toml` with `[build-system]` using `hatchling` (or `setuptools`).
- A `[project.scripts]` entry that maps `manim-mcp` → `manim_mcp.server:main`.
- The `src/` layout (PEP 517 compliant) so `uv` can build the wheel correctly.
- `mcp>=1.2.0` and `manim>=0.18.0` listed as runtime dependencies.

The target one-liner for Claude Code configuration must be achievable:

```json
{
  "mcpServers": {
    "manim": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/YOUR_ORG/manim-mcp.git", "manim-mcp"]
    }
  }
}
```

---

## 3. Tool Specifications

Each tool is defined with its MCP name, input schema, output schema, and behavioral contracts. Agent implementers should follow these precisely — the FastMCP `@mcp.tool()` decorator auto-generates the JSON Schema from Python type hints and docstrings, so naming and documentation are semantically significant.

---

### 3.1 `render_manim` (Core tool)

**Purpose:** Compile and render a Manim scene from Python source code into an MP4 video.

**Inputs:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `code` | `str` | required | Complete, self-contained Manim Python script |
| `scene_name` | `str` | `""` | Class name of the Scene to render; auto-detected if empty |
| `quality` | `Literal["low","medium","high","production"]` | `"medium"` | Render quality preset |
| `return_base64` | `bool` | `True` | Embed video bytes in response as base64 |
| `timeout` | `Optional[int]` | `None` | Per-render timeout override (falls back to `MANIM_TIMEOUT` env var) |

**Output schema:**

```python
{
    "success": bool,
    "video_path": str | None,       # Absolute path on disk
    "render_id": str | None,        # Deterministic content-addressed ID
    "duration_seconds": float,      # Wall-clock time for this render
    "quality": str,
    "scene_name": str,
    "cached": bool,                 # True if a prior render was reused
    "base64_video": str | None,     # Base64-encoded MP4 (if requested and under size limit)
    "preview_frame": str | None,    # v2.0: Base64-encoded PNG of final frame (always included)
    "error": str | None,            # Human-readable error summary (if failed)
    "manim_output": str,            # Full stderr tail (last 3000 chars) for debugging
    "diagnostics": list[dict],      # v2.0: Parsed error objects (see §3.6)
}
```

**Behavioral contracts:**

- Scene auto-detection MUST parse the code with a regex matching classes inheriting from any known Manim Scene base (`Scene`, `MovingCameraScene`, `ThreeDScene`, `ZoomedScene`, `VectorScene`, `LinearTransformationScene`). When multiple scenes are found, the first one in source order is selected.
- Caching: the render ID is `SHA-256(code + ":" + scene_name + ":" + quality)[:12]`. If an MP4 with that ID exists in `MANIM_OUTPUT_DIR`, it MUST be returned immediately without re-running Manim. The response MUST set `"cached": true`.
- Renders MUST run inside a fresh `tempfile.TemporaryDirectory`. The temp dir MUST be cleaned up after the MP4 is copied to `MANIM_OUTPUT_DIR`, even on failure.
- v2.0: After a successful render, the server MUST extract the final frame as a PNG using FFmpeg (`ffmpeg -sseof -0.1 -i video.mp4 -frames:v 1 preview.png`) and include it as `"preview_frame"` base64. This lets Claude "see" the result without streaming the full video.
- The tool MUST NOT raise Python exceptions that escape FastMCP. All subprocess errors, timeouts, and filesystem errors MUST be caught and returned as `{"success": false, "error": "..."}` responses.

---

### 3.2 `validate_manim_code` (Static analysis)

**Purpose:** Check Manim code for correctness without executing Manim. Returns in under 100ms.

**Inputs:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `code` | `str` | required | Manim Python source to validate |

**Output schema:**

```python
{
    "valid": bool,
    "errors": list[str],             # Blocking issues — render will definitely fail
    "warnings": list[str],           # Non-blocking issues — render may succeed but behave oddly
    "detected_scenes": list[str],    # Names of all Scene subclasses found
    "suggestions": list[str],        # v2.0: Improvement hints (style, performance)
}
```

**Validation checks (MUST implement):**

The validator MUST run the following checks in order, stopping and returning immediately on a `SyntaxError` since subsequent checks would produce noisy false positives on malformed AST.

- Python syntax via `compile(code, "<manim_code>", "exec")`.
- Presence of at least one Manim import (`from manim import` or `import manim`).
- Presence of at least one Scene subclass (see §3.1 for the regex pattern).
- Presence of a `def construct(self` method.
- Empty `self.play()` call (will raise `ValueError: at least one animation is required`).
- Use of deprecated Manim APIs: `ShowCreation` (replaced by `Create`), `FadeInFrom` (replaced by `FadeIn(shift=...)`), `ApplyMethod` (replaced by `.animate`). Each deprecated call should produce a warning with the modern equivalent.

**v2.0 additional checks:**

- Detect `self.wait(0)` and warn that it is a no-op.
- Detect objects created but never added with `self.add()` or played with `self.play()` — these are ghost objects that produce no output. This is a heuristic: extract variable names from assignments and check if they appear in a `self.add/play` call.
- Detect `ThreeDScene` usage and suggest enabling `renderer="opengl"` for better performance.

---

### 3.3 `render_manim_batch` (v2.0 — new)

**Purpose:** Render multiple scenes from the same script in a single tool call. Reduces round-trips for scripts that define several scenes.

**Inputs:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `code` | `str` | required | Manim Python script containing multiple Scene classes |
| `scene_names` | `list[str]` | `[]` | Specific scenes to render; if empty, render ALL detected scenes |
| `quality` | `str` | `"medium"` | Applied uniformly to all scenes in the batch |
| `max_parallel` | `int` | `2` | How many renders to run concurrently (capped at 4) |

**Output schema:**

```python
{
    "total": int,
    "succeeded": int,
    "failed": int,
    "results": [
        {
            "scene_name": str,
            "success": bool,
            "video_path": str | None,
            "render_id": str | None,
            "duration_seconds": float,
            "preview_frame": str | None,
            "error": str | None,
        }
    ]
}
```

**Behavioral contracts:**

- Parallel rendering MUST use `asyncio.gather` with a `Semaphore(max_parallel)` to cap concurrency. Concurrent renders share the same `MANIM_OUTPUT_DIR` but each gets its own `tempfile.TemporaryDirectory`.
- If a scene fails, the batch MUST continue rendering the remaining scenes. The `failed` counter MUST accurately reflect how many scenes did not produce output.
- Individual caching still applies: scenes with matching render IDs in `MANIM_OUTPUT_DIR` MUST be skipped.

---

### 3.4 `suggest_quality` (v2.0 — new)

**Purpose:** Recommend an appropriate quality level based on code complexity, animation count, and intended use case. Helps users avoid accidentally kicking off a 20-minute production render when they just want to iterate.

**Inputs:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `code` | `str` | required | Manim source code to analyze |
| `intended_use` | `Literal["iteration", "review", "sharing", "publication"]` | `"iteration"` | What the render is for |

**Output schema:**

```python
{
    "recommended_quality": str,        # One of "low", "medium", "high", "production"
    "estimated_render_seconds": dict,  # Keys: quality levels, values: rough second estimates
    "reasoning": str,                  # Human-readable explanation
    "complexity_score": int,           # 1–10 subjective complexity estimate
}
```

**Heuristics:**

Complexity score is computed by counting: number of `self.play()` calls (each +1), number of `MathTex`/`Tex` objects (+2 each, since LaTeX compilation is slow), use of `ThreeDScene` (+3), use of `ValueTracker` with `always_redraw` (+2), total lines of code (log₂ of line count). Recommended quality maps as: score ≤ 5 → `low` or `medium`, score ≤ 8 → `medium`, score > 8 → start with `low`, note `high` for final. Estimated seconds are rough multipliers: low×1, medium×4, high×10, production×40 relative to a baseline of `complexity_score * 2` seconds for `low` quality.

---

### 3.5 `list_renders`, `get_render_info`, `cleanup_renders`

These tools are fully specified by the v0.2 implementation in `server.py`. No behavioral changes are required for v2.0. The following additions MUST be made:

- `list_renders` MUST accept an optional `filter_scene` parameter to return only renders whose `render_id` contains the given scene name.
- `get_render_info` MUST include a `"preview_frame"` field (base64 PNG) in its response when `include_base64=True`, extracted from the stored MP4 via FFmpeg if not already cached as a `.png` sidecar file.
- `cleanup_renders` MUST also delete `.png` preview sidecar files when deleting their parent MP4.

---

### 3.6 Diagnostics Engine (v2.0 — cross-cutting concern)

A key weakness of v0.2 is that when Manim fails, the server returns raw stderr which can be hundreds of lines of Cairo/Pango/LaTeX spew that is hard for Claude to parse. v2.0 MUST implement a `DiagnosticsEngine` that post-processes stderr into structured, actionable objects.

**Diagnostic object schema:**

```python
{
    "code": str,               # Machine-readable error code (see table below)
    "severity": str,           # "error" | "warning"  
    "message": str,            # Human-readable description
    "line": int | None,        # Line number in user's code, if detectable
    "suggestion": str,         # Specific fix to apply
}
```

**Required error codes and detection patterns:**

| Code | Pattern to detect | Suggestion |
|---|---|---|
| `LATEX_NOT_FOUND` | `latex: command not found` OR `xelatex` not found | Install a LaTeX distribution (mactex on macOS, texlive on Linux) |
| `LATEX_SYNTAX_ERROR` | `LaTeX Error:` in stderr | Check the MathTex/Tex string at the indicated line for unescaped special chars |
| `IMPORT_ERROR` | `ModuleNotFoundError` | The named module is not installed; suggest `pip install <module>` |
| `NAME_ERROR` | `NameError: name '...' is not defined` | Extract the undefined name; suggest checking for typo or missing import |
| `CONSTRUCT_MISSING` | `has no attribute 'construct'` | Add `def construct(self): ...` to the Scene class |
| `EMPTY_PLAY` | `at least one animation` | Replace `self.play()` with `self.play(SomeAnimation(...))` |
| `DEPRECATION` | `DeprecationWarning` in Manim output | Show the deprecated API and its modern replacement |
| `RENDER_TIMEOUT` | Detected internally (asyncio.TimeoutError) | Suggest using `quality="low"` or splitting into multiple scenes |
| `FILE_NOT_FOUND` | `FileNotFoundError` | The script referenced a file (image, audio) that does not exist |
| `CAIRO_ERROR` | `cairo.Error` or `CairoError` | Usually a missing system library; suggest reinstalling system dependencies |

The `DiagnosticsEngine` MUST be a separate class/module, not inline logic in the tool function, so it can be independently tested and extended.

---

## 4. Configuration Reference

All configuration MUST be possible via environment variables so the server is stateless and easy to deploy in containers or cloud environments. No configuration file format is required — env vars are the contract.

| Variable | Type | Default | Description |
|---|---|---|---|
| `MANIM_OUTPUT_DIR` | path | `~/.manim-mcp/renders` | Persistent storage for rendered MP4s and PNG sidecars |
| `MANIM_TIMEOUT` | int | `120` | Global render timeout in seconds |
| `MANIM_EXECUTABLE` | str | `manim` | Path to the `manim` CLI binary |
| `MANIM_RETURN_BASE64` | `"0"` or `"1"` | `"1"` | Whether to embed video bytes by default |
| `MANIM_MAX_BASE64_BYTES` | int | `20971520` | Max file size (bytes) to embed as base64 (default 20 MB) |
| `MANIM_LOG_LEVEL` | str | `"INFO"` | Python logging level for stderr output |
| `MANIM_TRANSPORT` | `"stdio"` or `"sse"` | `"stdio"` | Transport protocol (stdio for Claude Code/Desktop) |
| `MANIM_MAX_PARALLEL` | int | `2` | Default concurrency cap for `render_manim_batch` |
| `MANIM_PREVIEW_FRAME` | `"0"` or `"1"` | `"1"` | Whether to extract a PNG preview frame after each render |

---

## 5. Caching Architecture

### 5.1 Content-Addressed Storage

Every render is identified by a 12-character hex prefix of `SHA-256(code + ":" + scene_name + ":" + quality)`. This makes the cache semantically meaningful: the same logical animation always produces the same ID, regardless of when or where it was rendered.

The cache lookup happens BEFORE launching any subprocess. If `{MANIM_OUTPUT_DIR}/{render_id}.mp4` exists, the server MUST return it immediately. This is a critical UX property: iterating on different parts of a larger Manim script (changing one scene) should not re-render unchanged scenes.

### 5.2 Sidecar Files

For each MP4 in `MANIM_OUTPUT_DIR`, the server MAY maintain a sidecar JSON file `{render_id}.json` containing:

```json
{
    "render_id": "...",
    "scene_name": "...",
    "quality": "...",
    "rendered_at": "ISO-8601 timestamp",
    "duration_seconds": 12.4,
    "code_sha256": "full 64-char hash"
}
```

This allows `list_renders` to return rich metadata without parsing render IDs or re-running FFmpeg. The sidecar file is written atomically (write to `.tmp` then rename) to prevent corruption if the server is killed mid-render.

### 5.3 Cache Invalidation

There is no TTL-based invalidation. The cache is invalidated only by `cleanup_renders`. This is intentional: Manim renders are expensive and deterministic, so there is never a reason to re-render identical code automatically.

---

## 6. Security Considerations

The server executes arbitrary user-provided Python code via the `manim` CLI. This is an inherent and intentional property of the tool — Manim is a code execution environment. The following mitigations MUST be documented clearly in the README and SHOULD be implemented:

- **Process isolation:** The Manim subprocess runs with the same OS user as the MCP server. For production deployments, consider running the server inside a container or as a dedicated low-privilege user.
- **Timeout enforcement:** The `MANIM_TIMEOUT` env var MUST be enforced via `asyncio.wait_for` with `proc.kill()` on expiry. A hung render MUST NOT block the MCP server indefinitely.
- **Output directory confinement:** The server MUST resolve `MANIM_OUTPUT_DIR` to an absolute path at startup and validate that it is a directory (creating it if it does not exist). It MUST NOT follow symlinks to paths outside the configured directory.
- **No network access from renders:** Manim does not require network access at render time. Implementers SHOULD document how to set up a firewall rule or container network policy to block outbound network access from the render subprocess.
- **Subprocess command injection:** The scene name passed to the Manim CLI MUST be validated as a Python identifier (`re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', scene_name)`) before being interpolated into the subprocess argument list. Invalid names MUST produce a validation error, not be passed to the shell.

---

## 7. Testing Requirements

The test suite MUST achieve the following without requiring Manim to be installed:

- **Unit tests** for all static analysis functions (`_extract_scene_names`, `_render_id`, `DiagnosticsEngine` pattern matching, `suggest_quality` heuristics).
- **Async tool tests** for `validate_manim_code`, `list_renders`, `cleanup_renders`, and `get_render_info` using real filesystem operations in `tmp_path` fixtures.
- **Mock subprocess tests** for `render_manim` that verify the happy path (success), timeout handling, Manim-exits-non-zero handling, and video-not-found-despite-success handling.
- **Integration tests** (marked `@pytest.mark.integration`, skipped in CI unless `MANIM_INTEGRATION=1`) that run actual Manim renders on a trivial scene and verify MP4 output exists and is non-empty.
- **Diagnostic engine tests** that feed known stderr strings through `DiagnosticsEngine` and assert the correct error codes are produced.

Coverage target: 85% line coverage on the `src/manim_mcp/` package, excluding `server.py`'s `main()` entry point.

---

## 8. Implementation Checklist for Agent Teams

The following represents a linear task ordering suitable for a coding agent or a two-agent team (one writing code, one reviewing and running tests).

**Phase 1 — Scaffolding (start here)**
- [ ] Verify `pyproject.toml` builds correctly: `uv build` should produce a wheel with `manim-mcp` entry point.
- [ ] Confirm `uvx --from . manim-mcp --help` (or equivalent) works from the repo root.
- [ ] Run the existing test suite: `pytest tests/ -v` — all tests should pass.

**Phase 2 — DiagnosticsEngine**
- [ ] Create `src/manim_mcp/diagnostics.py` with `DiagnosticsEngine` class.
- [ ] Implement all 10 error code patterns from §3.6.
- [ ] Write `tests/test_diagnostics.py` with one test per error code.
- [ ] Integrate into `render_manim`: pass `manim_output` through `DiagnosticsEngine` and include `diagnostics` in the response dict.

**Phase 3 — Preview frames**
- [ ] Add `_extract_preview_frame(mp4_path: Path) -> Optional[str]` function that calls FFmpeg.
- [ ] Call it from `render_manim` after successful render; include result as `preview_frame` in response.
- [ ] Cache the preview as `{render_id}.png` sidecar alongside the MP4.
- [ ] Add tests for frame extraction with a mock FFmpeg subprocess.

**Phase 4 — `suggest_quality` tool**
- [ ] Implement `suggest_quality` per §3.4 heuristics.
- [ ] Write unit tests covering: simple scene (score ≤ 3), heavy LaTeX scene (score ≥ 8), ThreeDScene bonus.

**Phase 5 — `render_manim_batch` tool**
- [ ] Implement `render_manim_batch` per §3.3 with `asyncio.gather` and `Semaphore`.
- [ ] Write tests covering: all-succeed case, partial-failure case, cached-scene case.

**Phase 6 — Sidecar JSON metadata**
- [ ] Write sidecar `{render_id}.json` on each fresh render.
- [ ] Update `list_renders` to read sidecars for rich metadata.
- [ ] Update `cleanup_renders` to also delete `.json` and `.png` sidecars.

**Phase 7 — Validation improvements**
- [ ] Add deprecated API detection to `validate_manim_code`.
- [ ] Add ghost-object detection heuristic.
- [ ] Add `ThreeDScene` + OpenGL suggestion.

**Phase 8 — Polish**
- [ ] Verify all logging uses `sys.stderr`, none to `sys.stdout`.
- [ ] Run `ruff check src/` and fix all lints.
- [ ] Update README with v2.0 tool descriptions and new environment variables.
- [ ] Confirm full test suite passes: `pytest tests/ -v --cov=src/manim_mcp`.

---

## 9. Future Roadmap (Out of Scope for v2.0)

These items are explicitly deferred but should inform architectural decisions now:

- **Remote rendering farm**: An HTTP/SSE mode that accepts render requests and dispatches to a pool of worker processes or containers, enabling parallelism beyond what a single developer machine supports.
- **Animation diffing**: Given two versions of Manim code, render both, extract frame sequences, and compute a visual diff to highlight what changed.
- **Voice narration overlay**: Accept a script alongside Manim code, generate TTS audio via an external API, and mux it with the rendered video using FFmpeg.
- **Interactive parameter sweeps**: Accept a parameter dict and code template, render multiple versions (e.g., showing a function with different parameters), and stitch them into a single video.
- **Manim Slides integration**: Support the `manim-slides` presentation framework, which compiles Manim animations into interactive HTML presentations.

---

## Appendix A: Manim Quality Flag Reference

| Level | CLI flag | Resolution | FPS | Typical render time (simple scene) |
|---|---|---|---|---|
| `low` | `-ql` | 480p | 15 | 3–8 seconds |
| `medium` | `-qm` | 720p | 30 | 10–25 seconds |
| `high` | `-qh` | 1080p | 60 | 30–90 seconds |
| `production` | `-qp` | 2160p (4K) | 60 | 5–20 minutes |

## Appendix B: Key Manim Scene Base Classes

Agent implementations should recognize all of these as valid Scene parents in the regex pattern:

`Scene`, `MovingCameraScene`, `ThreeDScene`, `ZoomedScene`, `VectorScene`, `LinearTransformationScene`, `ReconfigurableScene`, `SpecialThreeDScene`

## Appendix C: Known Platform Gotchas

- **macOS Apple Silicon**: Mixing x86 and arm64 Python binaries causes silent Cairo failures. Ensure Python, Cairo, and Manim are all from the same architecture.
- **Conda environments on Windows**: The `manim` executable path inside conda is not on the system PATH by default. Use `MANIM_EXECUTABLE` to point at the full path, e.g. `C:\Users\you\anaconda3\envs\manim\Scripts\manim.exe`.
- **LaTeX on Linux CI**: `texlive-latex-extra` alone is often insufficient. `dvipng` and `cm-super` packages are also required for `MathTex` to work correctly.
- **FFmpeg version**: Manim requires FFmpeg ≥ 4.0. The system FFmpeg on older Ubuntu LTS (18.04) is 3.x. Use a PPA or snap to get a newer version.
