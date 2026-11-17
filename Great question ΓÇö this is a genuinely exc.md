Great question — this is a genuinely exciting intersection of tools! Let me break it all down for you clearly.

---

## 🎬 What is Manim?

Manim (Mathematical Animation Engine) is the Python library that powers the famous 3Blue1Brown YouTube channel — think those gorgeous, flowing visualizations of calculus, linear algebra, and number theory. It was originally written by Grant Sanderson himself, then forked and maintained by the community as **Manim Community Edition** (the version you should use). It uses Cairo for 2D rendering and FFmpeg for video output, so it produces proper MP4s at up to 1080p60.

The key insight is that Manim is **deterministic and code-driven** — every animation is a Python class, making it a perfect target for an LLM to write and a server to execute.

---

## 🔌 What is MCP?

MCP (Model Context Protocol) is Anthropic's open protocol that gives Claude a structured "USB-C port" to the real world. Instead of Claude just outputting text, it can call **tools** exposed by MCP servers — things like "render this Manim script" or "search this database." Claude Code natively supports MCP servers configured via JSON files, which means you can wire a Manim rendering server directly into your Claude Code workflow.

---

## 🏆 The Best Repos to Use

There are three serious contenders, and they have meaningful differences:

**1. `Stelath/manim-mcp` — Best for Claude Code users (recommended!)**

This is the most polished and modern option. Its killer feature is that it supports installation via `uvx` (part of the `uv` Python toolchain), meaning you don't even need to clone the repo manually. The config for Claude Code is elegantly simple:

```json
{
  "mcpServers": {
    "manim": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/Stelath/manim-mcp.git", "manim-mcp"]
    }
  }
}
```

It supports multiple quality levels (480p → 720p → 1080p), includes example templates for equations, graphs, and geometry, and even has `.mcpb` bundle files for one-click installs in Claude Desktop. It's MIT licensed and actively maintained.

**2. `abhiemj/manim-mcp-server` — Most widely documented**

This is the most referenced repo across tutorials and the MCP server directories. It's simpler under the hood — a single `manim_server.py` script that you point Claude at — but requires more manual setup (absolute paths, `MANIM_EXECUTABLE` env variable). Good for learning the internals. The config pattern looks like:

```json
{
  "mcpServers": {
    "manim-server": {
      "command": "/absolute/path/to/python",
      "args": ["/absolute/path/to/manim-mcp-server/src/manim_server.py"],
      "env": { "MANIM_EXECUTABLE": "/path/to/manim" }
    }
  }
}
```

**3. `OMCHOKSI108/MCP_6` — Most ambitious / production-flavored**

This repo takes a more production-minded approach, returning video artifact URLs directly into the chat and supporting a `quality` parameter (`"low"`, `"medium"`, `"high"`, `"production"`). The tool schema is well-designed and explicitly expects `scene_name` alongside `manim_code`, which helps Claude generate cleaner, more targeted scripts.

---

## 🛠️ Technical Setup for Claude Code

For Claude Code specifically, you configure MCP in one of three scopes. For a personal Manim tool you'd use everywhere, add it at **user scope** in `~/.claude/mcp.json`. For a project-specific setup committed to version control, use `.mcp.json` at the project root.

The system dependencies you must have installed first are Cairo (for SVG/vector rendering), Pango (for text layout), FFmpeg (for video encoding), and a LaTeX distribution if you want mathematical typesetting. On macOS: `brew install cairo pango ffmpeg` plus `brew install --cask mactex`. On Linux: `sudo apt-get install libcairo2-dev libpango1.0-dev ffmpeg texlive-latex-extra`.

Then the full Claude Code setup with `Stelath/manim-mcp` is just:

```bash
# Install system deps first, then:
claude mcp add-json manim '{"command":"uvx","args":["--from","git+https://github.com/Stelath/manim-mcp.git","manim-mcp"]}'
```

That's it — Claude Code will now have a `render_manim` tool available and can write + render animations on demand when you describe what you want.

---

## 💡 Pro Tips

The workflow that makes this magical is: you describe the animation conceptually → Claude writes the Manim Python class → the MCP server executes it → the MP4 comes back. Claude is surprisingly good at Manim because the syntax is well-represented in its training data, especially the core patterns like `self.play(Write(equation))`, `Create()`, `Transform()`, and `FadeIn()`.

One gotcha: Manim renders can take 10–60 seconds even for simple scenes, so don't be surprised by the latency. The `low` quality (480p) preset is great for iteration, and you switch to `high` for the final version.

If you're on a Mac with Apple Silicon, make sure your Python environment matches your architecture — mixing x86 and arm64 Python/Cairo binaries is the most common silent failure point.

Would you like a step-by-step walkthrough of the actual setup on your specific OS, or want to see what kind of Manim scenes Claude tends to generate best?


###
Stelath/manim-mcp is out of commission. can you replicate the gist, esp the technical gist of it?! perhaps using abhiemj/manim-mcp-server for assistance and augmentation. or atleast create a PRD/ spec for another agent/ agent team?


What You Have
Five files that constitute a working, publishable MCP server:
server.py is the beating heart — a ~250-line FastMCP server using the official Anthropic MCP Python SDK. It exposes five tools (render_manim, validate_manim_code, list_renders, get_render_info, cleanup_renders) and is fully async so long renders don't block the event loop. Every design decision that made Stelath's version feel magical is replicated here.
pyproject.toml is arguably the most important file. The critical insight about Stelath's server was that it worked via uvx — no cloning, no PATH wrangling, just a JSON config line. That magic lives entirely in [project.scripts], which maps the manim-mcp entry point to manim_mcp.server:main. Without this, you're back to abhiemj's world of absolute paths.
PRD.md is a full v2.0 specification designed for an agent team to implement against. It defines four new tools (render_manim_batch, suggest_quality, and extensions to existing tools), a DiagnosticsEngine that converts raw Manim stderr into structured, actionable error objects, a sidecar caching architecture, and a phased implementation checklist that a coding agent can execute linearly.
README.md covers the system prerequisites (Cairo, Pango, FFmpeg, LaTeX) and both installation paths — uvx for elegance, traditional pip for visibility.
test_server.py covers all the pure-Python logic and uses mock subprocesses for the rendering path, so Manim doesn't need to be installed to run the tests. This is essential for CI.

The Key Technical Decisions Explained
The biggest thing the Stelath server did right that abhiemj didn't was the uvx packaging. To understand why this matters: Claude Code reads ~/.claude/mcp.json and spawns the MCP server process itself. If your config says "command": "python", "args": ["/absolute/path/to/manim_server.py"], it breaks the moment someone clones to a different directory, or the venv path changes, or they're on Windows. The uvx pattern fixes all of that because uv handles the virtualenv and entry point resolution automatically — the user literally never touches Python paths.
The second key decision is using asyncio.create_subprocess_exec instead of subprocess.run. This is subtle but important: Manim renders can take 10–90 seconds. If you block on a synchronous subprocess call, the FastMCP event loop stalls and the MCP connection appears dead to Claude. The async approach keeps the server heartbeating properly throughout.
Content-addressed caching via SHA-256 of (code + scene_name + quality) means iterating on a Manim script is fast — if you change Scene B but not Scene A, Scene A is returned from disk instantly. This was in Stelath's design and it's worth preserving.
The logging-to-stderr rule is the most critical correctness concern. On stdio-transport MCP servers, stdout IS the JSON-RPC communication channel. A single stray print() statement corrupts the JSON stream and breaks Claude's connection silently. Every log call in the implementation explicitly uses sys.stderr.

What to Do Next
To get this running today with the v0.2 implementation, push this to a GitHub repo and add the uvx config line to your ~/.claude/mcp.json. Install the system dependencies first (brew install cairo pango ffmpeg on Mac, then brew install --cask mactex for LaTeX). Then try telling Claude Code to "animate a visual proof that the sum of angles in a triangle equals 180 degrees, using low quality first."
The PRD's Phase 1–8 checklist then gives a coding agent (or you, or another Claude session with Claude Code) a clean linear path to the v2.0 feature set — particularly the DiagnosticsEngine, which will make the render→error→fix loop dramatically faster in practice.



###
only url content on stelath, since offline

Manim MCP Server
A Model Context Protocol (MCP) server that enables Claude Desktop to create mathematical animations using Manim (Mathematical Animation Engine).

This server allows Claude to generate video artifacts of mathematical explanations, making it easy to visualize complex mathematical concepts through animations.

Features
Create Math Animations: Generate mathematical animations by providing Manim scene code

Multiple Quality Options: Render videos in low (480p), medium (720p), or high (1080p) quality

Example Templates: Get example code for common animation types (equations, graphs, geometry, etc.)

Easy Integration: Works seamlessly with Claude Desktop through MCP

Installation
Option 1: MCPB Bundle (Easiest - One-Click Install)
For end users - Recommended!

Download the latest .mcpb file from Releases

Double-click the .mcpb file (or drag-and-drop into Claude Desktop)

Follow the installation prompts in Claude Desktop

Install system dependencies (see below)

MCPB bundles provide:

✅ One-click installation in Claude Desktop

✅ No manual configuration required

✅ Automatic updates

✅ Easy uninstall

Building MCPB yourself: See MCPB_BUILD.md for instructions on creating your own .mcpb bundle.

Option 2: Direct Install (For Developers)
Install from GitHub

pip install git+https://github.com/Stelath/manim-mcp.git

Install from Local Clone

git clone https://github.com/Stelath/manim-mcp.git
cd manim-mcp
./install.sh  # On macOS/Linux
# OR
install.bat   # On Windows

Using uvx (Isolated environments)

uvx --from git+https://github.com/Stelath/manim-mcp.git manim-mcp

This will install:

manim-mcp - The MCP server command

manim - The Manim Community Edition library

mcp - The Model Context Protocol SDK

Prerequisites
Python 3.10 or higher

Claude Desktop

Additional System Dependencies
Manim requires some system dependencies. Install them based on your OS:

macOS:

brew install py3cairo ffmpeg
brew install --cask mactex-no-gui

Ubuntu/Debian:

sudo apt-get update
sudo apt-get install build-essential python3-dev libcairo2-dev libpango1.0-dev ffmpeg
sudo apt-get install texlive texlive-latex-extra

Windows:

Install Chocolatey

Run: choco install manimce

For detailed installation instructions, see the Manim installation guide.

Configuration
MCPB Users (Option 1)
No manual configuration needed! The .mcpb bundle handles configuration automatically.

Manual Configuration (Option 2 - For Direct Install Only)
If you installed via pip/uvx, add this server to your Claude Desktop configuration file:

macOS: ~/Library/Application Support/Claude/claude_desktop_config.json

Windows: %APPDATA%\Claude\claude_desktop_config.json

Linux: ~/.config/Claude/claude_desktop_config.json

Add the following to your configuration:

{
  "mcpServers": {
    "manim": {
      "command": "manim-mcp"
    }
  }
}

That's it! Just one line. No paths, no environment variables needed.

Alternative: Using uvx (for direct GitHub installation without pip)

{
  "mcpServers": {
    "manim": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/Stelath/manim-mcp.git",
        "manim-mcp"
      ]
    }
  }
}

Restart Claude Desktop
After updating the configuration, restart Claude Desktop for the changes to take effect.

Usage
Once configured, you can ask Claude to create mathematical animations. Here are some examples:

Example 1: Simple Text Animation
Create a Manim animation that displays "Hello, Mathematics!" and then fades out.

Example 2: Mathematical Equation
Create a Manim animation showing Euler's identity: e^(iπ) + 1 = 0
Animate the equation being written, then highlight it.

Example 3: Graph Visualization
Create a Manim animation of a sine wave being drawn on a coordinate system,
with the equation y = sin(x) labeled.

Example 4: Geometric Transformation
Create a Manim animation showing a circle transforming into a square,
then into a triangle, demonstrating geometric morphing.

Example 5: Calculus Visualization
Create a Manim animation showing the area under the curve y = x^2 from 0 to 2,
illustrating the concept of integration.

Available Tools
The server exposes the following MCP tools:

create_math_animation
Create and render a mathematical animation.

Parameters:

scene_code (required): Python code defining a Manim Scene class

scene_name (required): Name of the Scene class to render

quality (optional): Render quality - "low", "medium" (default), or "high"

output_filename (optional): Custom filename for the output video

Returns: Path to the generated video file

get_manim_example
Get example Manim code for common animation types.

Parameters:

example_type (required): One of:

basic_text - Simple text animation

equation - Mathematical equation

graph - Function graph

geometry - Geometric shapes

transformation - Shape transformations

calculus - Calculus visualization

Returns: Example code and usage instructions

Output Location
Generated videos are saved to: {system_temp_dir}/manim_mcp_output/

macOS/Linux: /tmp/manim_mcp_output/

Windows: C:\Users\{username}\AppData\Local\Temp\manim_mcp_output\

Troubleshooting
Server Not Appearing in Claude Desktop
Check that the configuration file path is correct

Verify the Python path in the configuration

Restart Claude Desktop completely

Check Claude Desktop logs for errors

Manim Rendering Errors
Ensure all system dependencies are installed (ffmpeg, LaTeX, Cairo)

Test Manim independently: manim --version

Check the error messages returned by the tool

Import Errors
Verify the package is installed: pip show manim mcp

Check that PYTHONPATH includes the src directory

Try reinstalling: pip install -e . --force-reinstall

Development
Building MCPB Bundles
To create a .mcpb bundle for distribution:

Install MCPB CLI:

npm install -g @anthropic-ai/mcpb

Ensure icon.png exists (512x512 PNG file)

Build the bundle:

./build_mcpb.sh  # macOS/Linux
# OR
build_mcpb.bat   # Windows
# OR
mcpb pack        # Direct CLI

Test the bundle:

Double-click the generated .mcpb file

Or drag-and-drop into Claude Desktop

Verify both tools work correctly

For complete build instructions, see MCPB_BUILD.md.

Project Structure
manim-mcp/
├── manifest.json         # MCPB manifest
├── icon.png             # Extension icon
├── src/
│   └── manim_mcp/
│       ├── __init__.py
│       ├── __main__.py
│       └── server.py    # Main MCP server implementation
├── pyproject.toml       # Package configuration
├── README.md
├── MCPB_BUILD.md       # MCPB build guide
└── LICENSE

Running Tests
pytest

Code Formatting
black src/
ruff check src/

Learn More
Manim Community Documentation

MCP Documentation

Claude Desktop

License
See LICENSE file for details.

Contributing
Contributions are welcome! Please feel free to submit issues or pull requests.

Credits
Manim Community - Mathematical Animation Engine

Anthropic - Model Context Protocol and Claude

3Blue1Brown - Original Manim creator


