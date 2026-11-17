"""
manim-mcp: A production-grade MCP server for rendering Manim animations.

Architecture overview:
  - Uses FastMCP (official MCP Python SDK) for stdio transport
  - Exposes 5 tools: render_manim, validate_manim_code, list_renders,
    get_render_info, and cleanup_renders
  - Renders run as sandboxed subprocesses with configurable timeouts
  - Output videos land in a persistent MANIM_OUTPUT_DIR
  - All logging goes to stderr so stdout stays clean for JSON-RPC
"""

import asyncio
import base64
import hashlib
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Literal, Optional

from mcp.server.fastmcp import FastMCP

# ── Logging: MUST go to stderr on stdio-transport servers ──────────────────
logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="[manim-mcp] %(levelname)s %(message)s",
)
log = logging.getLogger("manim-mcp")

# ── Environment-variable configuration ────────────────────────────────────
# These let the user tune the server without editing source code.

# Where rendered videos are stored permanently (survives cleanup of temp dirs)
OUTPUT_DIR = Path(
    os.environ.get("MANIM_OUTPUT_DIR", Path.home() / ".manim-mcp" / "renders")
)

# How long (seconds) to wait for Manim before killing the process
RENDER_TIMEOUT = int(os.environ.get("MANIM_TIMEOUT", "120"))

# Override the manim executable (useful inside conda envs or virtualenvs)
MANIM_EXECUTABLE = os.environ.get("MANIM_EXECUTABLE", "manim")

# Whether to return base64-encoded video bytes in the tool response.
# Useful for Claude Desktop which can show inline video; set to "0" to disable.
RETURN_BASE64 = os.environ.get("MANIM_RETURN_BASE64", "1") == "1"

# Maximum file size (bytes) to embed as base64 — default 20 MB
MAX_BASE64_BYTES = int(os.environ.get("MANIM_MAX_BASE64_BYTES", str(20 * 1024 * 1024)))

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Quality flag mapping ───────────────────────────────────────────────────
# Manim's -q flag controls both resolution and frame rate.
QUALITY_FLAGS = {
    "low":        ["-ql"],   # 480p  @ 15 fps  — fast iteration
    "medium":     ["-qm"],   # 720p  @ 30 fps  — review quality
    "high":       ["-qh"],   # 1080p @ 60 fps  — near-final
    "production": ["-qp"],   # 2160p @ 60 fps  — final output (slow!)
}

# ── FastMCP server instance ────────────────────────────────────────────────
mcp = FastMCP(
    "manim-mcp",
    instructions=(
        "Use render_manim to turn Manim Python code into an MP4 animation. "
        "Always pass a valid class name as scene_name. "
        "Use 'low' quality for quick iteration, 'high' or 'production' for finals. "
        "If rendering fails, check the error field — it will contain the full "
        "Manim stderr output so you can fix the code and retry."
    ),
)


# ── Helper utilities ───────────────────────────────────────────────────────

def _extract_scene_names(code: str) -> list[str]:
    """
    Parse Manim Python source and return all Scene subclass names.
    This lets us auto-detect scene_name when the user doesn't specify one.
    """
    # Manim scenes inherit from Scene, MovingCameraScene, ThreeDScene, etc.
    pattern = re.compile(
        r"^class\s+(\w+)\s*\(.*?(?:Scene|Camera)\w*\s*\)",
        re.MULTILINE,
    )
    return pattern.findall(code)


def _render_id(code: str, scene_name: str, quality: str) -> str:
    """
    Produce a short deterministic ID for a (code, scene, quality) triple.
    Used as the output filename so identical renders are cached on disk.
    """
    digest = hashlib.sha256(f"{code}:{scene_name}:{quality}".encode()).hexdigest()[:12]
    return f"{scene_name}_{quality}_{digest}"


def _find_output_video(search_root: Path) -> Optional[Path]:
    """
    Manim puts its output inside a deeply nested directory structure like:
      media/videos/<script_stem>/<resolution>/SceneName.mp4
    We just glob for the first MP4 we can find after the render completes.
    """
    videos = list(search_root.rglob("*.mp4"))
    if not videos:
        # Also look for .gif and .webm in case someone uses those renderers
        videos = list(search_root.rglob("*.gif")) + list(search_root.rglob("*.webm"))
    return videos[0] if videos else None


async def _run_manim(
    script_path: Path,
    scene_name: str,
    quality: str,
    work_dir: Path,
) -> tuple[bool, str, Optional[Path]]:
    """
    Execute Manim as an async subprocess and return (success, stderr_text, video_path).

    We use asyncio.create_subprocess_exec instead of subprocess.run so the
    MCP server event loop stays responsive during long renders.
    """
    quality_flag = QUALITY_FLAGS.get(quality, ["-qm"])
    cmd = [
        MANIM_EXECUTABLE,
        *quality_flag,
        "--media_dir", str(work_dir / "media"),
        "--output_file", scene_name,   # keep filename predictable
        str(script_path),
        scene_name,
    ]
    log.info("Running: %s", " ".join(cmd))

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(work_dir),
        )
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(), timeout=RENDER_TIMEOUT
        )
    except asyncio.TimeoutError:
        proc.kill()
        return False, f"Render timed out after {RENDER_TIMEOUT}s", None
    except FileNotFoundError:
        return (
            False,
            f"Manim executable not found: '{MANIM_EXECUTABLE}'. "
            "Install with: pip install manim  (or set MANIM_EXECUTABLE env var)",
            None,
        )

    combined = stderr.decode(errors="replace") + stdout.decode(errors="replace")

    if proc.returncode != 0:
        return False, combined, None

    video = _find_output_video(work_dir / "media")
    if video is None:
        return False, f"Manim exited 0 but no video found.\n{combined}", None

    return True, combined, video


# ── Tool: render_manim ─────────────────────────────────────────────────────

@mcp.tool()
async def render_manim(
    code: str,
    scene_name: str = "",
    quality: Literal["low", "medium", "high", "production"] = "medium",
    return_base64: bool = True,
) -> dict:
    """
    Render a Manim animation scene from Python source code.

    Provide complete, self-contained Manim Python code. The code must define
    at least one class that inherits from a Manim Scene type and implements
    a construct() method.

    Args:
        code: Complete Manim Python script. Must include all necessary imports
              (e.g. 'from manim import *') and at least one Scene subclass.
        scene_name: The exact class name of the Scene to render. If omitted,
                    the server will auto-detect the first Scene class in the code.
        quality: Render quality — 'low' (480p/15fps, fastest), 'medium' (720p/30fps),
                 'high' (1080p/60fps), or 'production' (4K/60fps, slowest).
        return_base64: If True, include the video as a base64-encoded string in
                       the response (capped at MANIM_MAX_BASE64_BYTES). Set to
                       False when you only need the file path.

    Returns:
        A dict with keys: success, video_path, render_id, duration_seconds,
        quality, scene_name, base64_video (if requested), error (if failed),
        and manim_output (full stderr for debugging).
    """
    start = time.perf_counter()

    # ── Auto-detect scene name ──────────────────────────────────────────
    detected = _extract_scene_names(code)
    if not scene_name:
        if not detected:
            return {
                "success": False,
                "error": (
                    "Could not detect a Scene class in the provided code. "
                    "Make sure you have a class inheriting from Scene (or a subclass). "
                    "Detected classes: none"
                ),
            }
        scene_name = detected[0]
        log.info("Auto-detected scene: %s", scene_name)

    # ── Compute render ID and check if already on disk ──────────────────
    rid = _render_id(code, scene_name, quality)
    final_path = OUTPUT_DIR / f"{rid}.mp4"

    if final_path.exists():
        log.info("Cache hit — returning existing render: %s", final_path)
        elapsed = time.perf_counter() - start
        result = {
            "success": True,
            "video_path": str(final_path),
            "render_id": rid,
            "duration_seconds": round(elapsed, 2),
            "quality": quality,
            "scene_name": scene_name,
            "cached": True,
            "manim_output": "(cached, not re-rendered)",
        }
        if return_base64 and RETURN_BASE64:
            result["base64_video"] = _maybe_encode(final_path)
        return result

    # ── Write code to a temp directory and render ───────────────────────
    with tempfile.TemporaryDirectory(prefix="manim_mcp_") as tmpdir:
        work = Path(tmpdir)
        script = work / "scene.py"
        script.write_text(code, encoding="utf-8")

        success, output, video_path = await _run_manim(
            script, scene_name, quality, work
        )

        elapsed = time.perf_counter() - start

        if not success:
            return {
                "success": False,
                "error": output,
                "duration_seconds": round(elapsed, 2),
                "scene_name": scene_name,
                "quality": quality,
            }

        # Copy from the temp dir to the persistent output directory
        shutil.copy2(video_path, final_path)

    result = {
        "success": True,
        "video_path": str(final_path),
        "render_id": rid,
        "duration_seconds": round(elapsed, 2),
        "quality": quality,
        "scene_name": scene_name,
        "cached": False,
        "manim_output": output[-3000:],  # tail to keep response size sane
    }

    if return_base64 and RETURN_BASE64:
        result["base64_video"] = _maybe_encode(final_path)

    return result


def _maybe_encode(path: Path) -> Optional[str]:
    """Return base64 string if file is within size limit, else None."""
    size = path.stat().st_size
    if size > MAX_BASE64_BYTES:
        log.warning("Video %s is %.1f MB — too large to embed as base64", path, size / 1e6)
        return None
    return base64.b64encode(path.read_bytes()).decode("ascii")


# ── Tool: validate_manim_code ──────────────────────────────────────────────

@mcp.tool()
async def validate_manim_code(code: str) -> dict:
    """
    Statically validate Manim Python code without rendering.

    Runs a syntax check and inspects the code for common Manim mistakes
    (missing imports, no Scene class, etc.) — much faster than a full render.
    Useful for catching errors before committing to a slow high-quality render.

    Args:
        code: Manim Python source to validate.

    Returns:
        A dict with: valid (bool), errors (list of strings),
        warnings (list of strings), detected_scenes (list of class names).
    """
    errors = []
    warnings = []

    # 1. Python syntax check via compile()
    try:
        compile(code, "<manim_code>", "exec")
    except SyntaxError as e:
        errors.append(f"SyntaxError at line {e.lineno}: {e.msg}")
        return {"valid": False, "errors": errors, "warnings": warnings, "detected_scenes": []}

    # 2. Check for Manim import
    if "from manim import" not in code and "import manim" not in code:
        warnings.append(
            "No Manim import detected. Add 'from manim import *' at the top."
        )

    # 3. Check for at least one Scene class
    scenes = _extract_scene_names(code)
    if not scenes:
        errors.append(
            "No Scene subclass found. Define a class that inherits from Scene "
            "(e.g. 'class MyScene(Scene): ...')."
        )

    # 4. Check for construct() method
    if "def construct(self" not in code:
        errors.append(
            "No construct(self) method found. Manim requires each Scene to "
            "implement 'def construct(self): ...' where animations are defined."
        )

    # 5. Heuristic checks for common beginner mistakes
    if "self.play()" in code:
        warnings.append(
            "Empty self.play() call detected — this will raise a Manim error at runtime."
        )
    if "self.add(" in code and "self.play(" not in code:
        warnings.append(
            "You're using self.add() but no self.play() — your scene may render "
            "as a static image. Use self.play(Create(...)) to animate."
        )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "detected_scenes": scenes,
    }


# ── Tool: list_renders ─────────────────────────────────────────────────────

@mcp.tool()
async def list_renders() -> dict:
    """
    List all previously rendered Manim videos on disk.

    Returns metadata about each cached render: render_id, filename,
    file size in MB, and modification timestamp.
    """
    renders = []
    for p in sorted(OUTPUT_DIR.glob("*.mp4"), key=lambda f: f.stat().st_mtime, reverse=True):
        stat = p.stat()
        renders.append({
            "render_id": p.stem,
            "filename": p.name,
            "path": str(p),
            "size_mb": round(stat.st_size / 1e6, 2),
            "modified": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime)),
        })
    return {
        "render_count": len(renders),
        "output_dir": str(OUTPUT_DIR),
        "renders": renders,
    }


# ── Tool: get_render_info ──────────────────────────────────────────────────

@mcp.tool()
async def get_render_info(render_id: str, include_base64: bool = False) -> dict:
    """
    Retrieve metadata (and optionally the video bytes) for a specific render.

    Args:
        render_id: The render_id returned by a previous render_manim call.
        include_base64: If True, embed the video as base64 in the response.

    Returns:
        Metadata dict, plus base64_video if requested and file is within size limit.
    """
    path = OUTPUT_DIR / f"{render_id}.mp4"
    if not path.exists():
        return {"found": False, "render_id": render_id}

    stat = path.stat()
    result = {
        "found": True,
        "render_id": render_id,
        "path": str(path),
        "size_mb": round(stat.st_size / 1e6, 2),
        "modified": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime)),
    }
    if include_base64:
        result["base64_video"] = _maybe_encode(path)
    return result


# ── Tool: cleanup_renders ──────────────────────────────────────────────────

@mcp.tool()
async def cleanup_renders(keep_latest: int = 10) -> dict:
    """
    Delete old render files, keeping only the most recent N renders.

    Args:
        keep_latest: Number of most-recent renders to preserve (default 10).
                     Pass 0 to delete ALL renders.

    Returns:
        A summary of how many files were deleted and how much space was freed.
    """
    all_renders = sorted(
        OUTPUT_DIR.glob("*.mp4"),
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )
    to_delete = all_renders[keep_latest:]
    freed_bytes = 0
    deleted = []
    for p in to_delete:
        freed_bytes += p.stat().st_size
        p.unlink()
        deleted.append(p.name)

    return {
        "deleted_count": len(deleted),
        "freed_mb": round(freed_bytes / 1e6, 2),
        "kept_count": min(keep_latest, len(all_renders)),
        "deleted_files": deleted,
    }


# ── Entry point ────────────────────────────────────────────────────────────

def main():
    """Entry point registered in pyproject.toml so 'uvx manim-mcp' works."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
