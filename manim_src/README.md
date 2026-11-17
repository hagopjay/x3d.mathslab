# manim-mcp

A production-grade **Model Context Protocol server** for rendering [Manim Community Edition](https://www.manim.community/) animations — designed for seamless use with **Claude Code** and **Claude Desktop**.

Inspired by the now-archived `Stelath/manim-mcp`, rebuilt from first principles with improved error handling, proper packaging, async rendering, caching, and a full test suite.

---

## What This Does

`manim-mcp` gives Claude a `render_manim` tool. You describe an animation in natural language, Claude writes the Manim Python code, the MCP server executes it as a subprocess, and an MP4 video lands on your disk. Claude can also validate code before rendering, browse past renders, and clean up old files.

```
You → "Animate the Pythagorean theorem"
Claude → writes Manim code → calls render_manim tool → server runs Manim → MP4 returned
```

---

## System Prerequisites

These must be installed **before** the Python package:

**macOS (Homebrew):**
```bash
brew install cairo pango ffmpeg
brew install --cask mactex   # for LaTeX math typesetting (optional but recommended)
```

**Ubuntu / Debian:**
```bash
sudo apt-get install libcairo2-dev libpango1.0-dev ffmpeg texlive-latex-extra
```

**Windows:**
Install via [Chocolatey](https://chocolatey.org): `choco install ffmpeg` and install
MikTeX from https://miktex.org. Cairo/Pango come bundled with Manim's Windows install.

---

## Quick Install — Two Paths

### Path A: `uvx` (zero-clone, like Stelath's original)

This is the cleanest approach. `uv` handles the virtualenv and entry point automatically.

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install manim-mcp directly from this repo
uvx --from git+https://github.com/YOUR_ORG/manim-mcp.git manim-mcp
```

### Path B: Traditional pip install

```bash
git clone https://github.com/YOUR_ORG/manim-mcp.git
cd manim-mcp
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"           # -e for editable, [dev] for test dependencies
```

---

## Configuring Claude Code

Add this to your Claude Code MCP config. **User scope** (`~/.claude/mcp.json`) makes the tool available in every project:

```json
{
  "mcpServers": {
    "manim": {
      "command": "uvx",
      "args": [
        "--from", "git+https://github.com/YOUR_ORG/manim-mcp.git",
        "manim-mcp"
      ],
      "env": {
        "MANIM_OUTPUT_DIR": "/Users/you/manim-renders",
        "MANIM_TIMEOUT": "180"
      }
    }
  }
}
```

Or with a local pip install:

```json
{
  "mcpServers": {
    "manim": {
      "command": "/path/to/.venv/bin/python",
      "args": ["-m", "manim_mcp.server"],
      "env": {
        "MANIM_OUTPUT_DIR": "/Users/you/manim-renders"
      }
    }
  }
}
```

Via the CLI shorthand:
```bash
claude mcp add-json manim '{"command":"uvx","args":["--from","git+https://github.com/YOUR_ORG/manim-mcp.git","manim-mcp"]}'
```

---

## Environment Variables

| Variable | Default | Purpose |
|---|---|---|
| `MANIM_OUTPUT_DIR` | `~/.manim-mcp/renders` | Where MP4s are saved permanently |
| `MANIM_TIMEOUT` | `120` | Seconds before killing a hung render |
| `MANIM_EXECUTABLE` | `manim` | Path to manim CLI (useful in conda envs) |
| `MANIM_RETURN_BASE64` | `1` | Embed video bytes in response (set to `0` to disable) |
| `MANIM_MAX_BASE64_BYTES` | `20971520` | Max file size (bytes) to embed — default 20 MB |

---

## Available MCP Tools

### `render_manim`
The core tool. Accepts complete Manim Python source, a scene class name, and a quality level. Returns the video path, render metadata, and (if under 20 MB) base64-encoded video bytes.

**Quality levels** map directly to Manim's `-q` flag:
- `low` → 480p @ 15 fps (fastest — use for iteration)
- `medium` → 720p @ 30 fps (default — good balance)
- `high` → 1080p @ 60 fps (for sharing)
- `production` → 2160p @ 60 fps (slow — use for finals)

Renders are **content-addressed**: the same code + scene + quality always produces the same `render_id`, and the server skips re-rendering if that ID already exists on disk.

### `validate_manim_code`
Syntax-checks and heuristic-validates Manim code without running Manim. Catches missing imports, missing `construct()`, and common beginner mistakes in milliseconds rather than seconds.

### `list_renders`
Returns metadata for all videos in `MANIM_OUTPUT_DIR`, newest first.

### `get_render_info`
Retrieves metadata (and optionally the base64 bytes) for a specific `render_id`.

### `cleanup_renders`
Deletes old renders, keeping only the N most recent. Pass `keep_latest=0` to wipe everything.

---

## Example Prompts for Claude

Once configured, try these in Claude Code:

- *"Animate a visual proof of the Pythagorean theorem using Manim, medium quality."*
- *"Create a Manim scene showing a Fourier series approximation building up with more and more terms."*
- *"Make a 3D Manim animation of a rotating icosahedron, low quality first so I can check it."*
- *"List my recent Manim renders."*
- *"Clean up all but the last 5 renders."*

---

## Running Tests

```bash
cd manim-mcp
pip install -e ".[dev]"
pytest tests/ -v
```

The test suite mocks the Manim subprocess so **no Manim installation is needed to run tests**.

---

## Architecture Notes

The server uses `asyncio.create_subprocess_exec` rather than `subprocess.run` so the MCP event loop stays responsive during renders (which can take 10–60+ seconds). Each render runs in a temporary directory that is automatically cleaned up, with the final MP4 copied to the persistent `MANIM_OUTPUT_DIR`.

Render IDs are SHA-256 hashes of `code + scene_name + quality`, truncated to 12 hex characters. This gives you implicit caching: re-rendering identical code costs zero time.

All logging goes to `stderr`. This is critical — on stdio-transport MCP servers, anything written to `stdout` corrupts the JSON-RPC stream and silently breaks Claude's connection.

---

## License

MIT
