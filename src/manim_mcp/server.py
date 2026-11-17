"""
manim-mcp v2.1: Trusted-local Manim rendering adapter.

Manim executes supplied Python with the server user's privileges. Syntax
validation is a diagnostic aid, not isolation. Do not expose this tool to
untrusted callers or connect it to an arbitrary-code HTTP endpoint.

Architecture:
  - FastMCP (official Anthropic MCP Python SDK) over stdio transport
  - 7 tools: render_manim, render_manim_batch, validate_manim_code,
    suggest_quality, list_renders, get_render_info, cleanup_renders
  - DiagnosticsEngine: parses Manim stderr into structured error objects
  - Cache identity includes code, scene, quality and declared engine identity
  - Sidecar files: {id}.mp4 + {id}.png (preview frame) + {id}.json (metadata)
  - Scene name validation before subprocess interpolation (security)
  - Async subprocess rendering — event loop stays responsive during long renders
  - All logging → stderr; stdout is reserved for JSON-RPC
"""

import asyncio
import ast
import importlib.metadata
import platform
import signal
import weakref
import base64
import hashlib
import json
import logging
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, Optional

from mcp.server.fastmcp import FastMCP

# ── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(
    stream=sys.stderr,
    level=os.environ.get("MANIM_LOG_LEVEL", "INFO"),
    format="[manim-mcp] %(levelname)s %(message)s",
)
log = logging.getLogger("manim-mcp")

# ── Environment configuration ──────────────────────────────────────────────
OUTPUT_DIR = Path(
    os.environ.get("MANIM_OUTPUT_DIR", Path.home() / ".manim-mcp" / "renders")
).resolve()
def _env_int(name: str, default: int, minimum: int, maximum: int) -> int:
    try:
        value = int(os.environ.get(name, str(default)))
    except (TypeError, ValueError) as error:
        raise ValueError(f"{name} must be an integer in {minimum}..{maximum}") from error
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be an integer in {minimum}..{maximum}")
    return value


RENDER_TIMEOUT = _env_int("MANIM_TIMEOUT", 120, 1, 3600)
MANIM_EXECUTABLE = os.environ.get("MANIM_EXECUTABLE", "manim")
if not MANIM_EXECUTABLE or "\0" in MANIM_EXECUTABLE:
    raise ValueError("MANIM_EXECUTABLE must name an executable")
RETURN_BASE64 = os.environ.get("MANIM_RETURN_BASE64", "1") == "1"
MAX_BASE64_BYTES = _env_int("MANIM_MAX_BASE64_BYTES", 20 * 1024 * 1024, 0, 100 * 1024 * 1024)
EXTRACT_PREVIEW = os.environ.get("MANIM_PREVIEW_FRAME", "1") == "1"
MAX_PARALLEL = _env_int("MANIM_MAX_PARALLEL", 2, 1, 4)
MAX_CODE_BYTES = 256 * 1024
MAX_BATCH_SCENES = 16
_GLOBAL_RENDER_SEMAPHORE = asyncio.Semaphore(MAX_PARALLEL)
_RENDER_LOCKS: weakref.WeakValueDictionary = weakref.WeakValueDictionary()
_ACTIVE_RENDERS: set[str] = set()

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Quality flag mapping ───────────────────────────────────────────────────
QUALITY_FLAGS: dict[str, list[str]] = {
    "low":        ["-ql"],   # 480p  @ 15 fps
    "medium":     ["-qm"],   # 720p  @ 30 fps
    "high":       ["-qh"],   # 1080p @ 60 fps
    "production": ["-qp"],   # 2160p @ 60 fps
}

# ── FastMCP server ─────────────────────────────────────────────────────────
mcp = FastMCP(
    "manim-mcp",
    instructions=(
        "Trusted local use only: rendering executes supplied Python with host privileges. "
        "Static validation is not a sandbox. "
        "Use render_manim to turn Manim Python code into an MP4 animation. "
        "Always include a complete, self-contained script with 'from manim import *'. "
        "Use 'low' quality for iteration, 'high' or 'production' for finals. "
        "Call validate_manim_code first to catch errors before a slow render. "
        "Call suggest_quality to pick the right quality preset. "
        "Use render_manim_batch when a script defines multiple scenes to render at once."
    ),
)


# ══════════════════════════════════════════════════════════════════════════════
# DiagnosticsEngine
# ══════════════════════════════════════════════════════════════════════════════

class DiagnosticsEngine:
    """
    Converts raw Manim stderr into a list of structured diagnostic objects.

    Each diagnostic has: code, severity, message, line (if detectable), suggestion.
    This keeps the tool response size sane and gives Claude actionable fixes.
    """

    # (code, severity, pattern, suggestion)
    RULES: list[tuple[str, str, str, str]] = [
        (
            "LATEX_NOT_FOUND",
            "error",
            r"(latex|xelatex|pdflatex): command not found",
            "Install a LaTeX distribution: `brew install --cask mactex` (macOS) "
            "or `sudo apt-get install texlive-latex-extra` (Linux).",
        ),
        (
            "LATEX_SYNTAX_ERROR",
            "error",
            r"LaTeX Error:",
            "Check the MathTex/Tex string for unescaped special characters "
            "(e.g., use r'\\frac{1}{2}' not '\\frac{1}{2}').",
        ),
        (
            "IMPORT_ERROR",
            "error",
            r"ModuleNotFoundError: No module named '([^']+)'",
            "Install the missing module: `pip install {match_1}`.",
        ),
        (
            "NAME_ERROR",
            "error",
            r"NameError: name '([^']+)' is not defined",
            "'{match_1}' is undefined — check for a typo or a missing import.",
        ),
        (
            "CONSTRUCT_MISSING",
            "error",
            r"has no attribute 'construct'",
            "Add `def construct(self): ...` to your Scene class.",
        ),
        (
            "EMPTY_PLAY",
            "error",
            r"at least one animation",
            "Replace `self.play()` with `self.play(SomeAnimation(...))`.",
        ),
        (
            "DEPRECATION",
            "warning",
            r"DeprecationWarning",
            "A deprecated Manim API is in use. Check the Manim changelog for the modern equivalent.",
        ),
        (
            "FILE_NOT_FOUND",
            "error",
            r"FileNotFoundError",
            "The script references a file (image, audio) that does not exist at that path.",
        ),
        (
            "CAIRO_ERROR",
            "error",
            r"(cairo\.Error|CairoError)",
            "Cairo rendering error — try reinstalling system deps: "
            "`brew install cairo pango` (macOS).",
        ),
        (
            "ATTRIBUTE_ERROR",
            "error",
            r"AttributeError: '([^']+)' object has no attribute '([^']+)'",
            "'{match_1}' has no attribute '{match_2}'. Check spelling or Manim version.",
        ),
    ]

    @classmethod
    def parse(cls, stderr: str, timed_out: bool = False) -> list[dict]:
        diagnostics: list[dict] = []

        if timed_out:
            diagnostics.append({
                "code": "RENDER_TIMEOUT",
                "severity": "error",
                "message": f"Render exceeded the {RENDER_TIMEOUT}s timeout.",
                "line": None,
                "suggestion": (
                    f"Try quality='low' to speed up, or split your scene into smaller parts. "
                    f"You can also raise the timeout via MANIM_TIMEOUT env var (currently {RENDER_TIMEOUT}s)."
                ),
            })
            return diagnostics

        for code, severity, pattern, suggestion_template in cls.RULES:
            for match in re.finditer(pattern, stderr, re.IGNORECASE):
                # Fill {match_N} placeholders in suggestion
                suggestion = suggestion_template
                for i, g in enumerate(match.groups(), start=1):
                    suggestion = suggestion.replace(f"{{match_{i}}}", g or "")

                # Try to extract a line number from context around the match
                line_no = cls._find_line_number(stderr, match.start())

                diagnostics.append({
                    "code": code,
                    "severity": severity,
                    "message": match.group(0)[:200],
                    "line": line_no,
                    "suggestion": suggestion,
                })

        return diagnostics

    @staticmethod
    def _find_line_number(text: str, pos: int) -> Optional[int]:
        """Look backwards from pos for a 'line N' or 'File ..., line N' pattern."""
        snippet = text[max(0, pos - 300): pos + 100]
        m = re.search(r"line (\d+)", snippet, re.IGNORECASE)
        if m:
            return int(m.group(1))
        return None


# ══════════════════════════════════════════════════════════════════════════════
# Helper utilities
# ══════════════════════════════════════════════════════════════════════════════

_SCENE_BASES = {"Scene", "MovingCameraScene", "ThreeDScene", "ZoomedScene",
                "VectorScene", "LinearTransformationScene"}
_RENDER_ID = re.compile(r"[A-Za-z_][A-Za-z0-9_]{0,127}_(?:low|medium|high|production)_[0-9a-f]{12,64}\Z")


def _extract_scene_names(code: str) -> list[str]:
    """AST discovery, without importing/executing code; supports local inheritance."""
    if not isinstance(code, str) or len(code.encode()) > MAX_CODE_BYTES:
        return []
    try:
        tree = ast.parse(code)
    except (SyntaxError, ValueError, TypeError):
        return []
    names = set(_SCENE_BASES)
    modules = {"manim"}
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == "manim":
            names.update(alias.asname or alias.name for alias in node.names if alias.name in _SCENE_BASES)
        elif isinstance(node, ast.Import):
            modules.update(alias.asname or alias.name for alias in node.names if alias.name == "manim")
    classes = [node for node in tree.body if isinstance(node, ast.ClassDef)]
    found = set()
    for _ in classes:
        for node in classes:
            if any((isinstance(base, ast.Name) and base.id in names) or
                   (isinstance(base, ast.Attribute) and isinstance(base.value, ast.Name)
                    and base.value.id in modules and base.attr in _SCENE_BASES)
                   for base in node.bases):
                names.add(node.name)
                found.add(node.name)
    return [node.name for node in classes if node.name in found]


def _validate_identifier(name: str) -> bool:
    return isinstance(name, str) and bool(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,127}", name))


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _engine_identity() -> dict:
    """Declared cache context, not a complete dependency or hardware fingerprint."""
    resolved = shutil.which(MANIM_EXECUTABLE)
    binary = Path(resolved).resolve() if resolved else None
    try:
        version = importlib.metadata.version("manim")
    except importlib.metadata.PackageNotFoundError:
        version = "not-installed-in-server-interpreter"
    identity = {"executable": str(binary) if binary else MANIM_EXECUTABLE,
                "manim_distribution": version, "server_python": platform.python_version(),
                "cache_epoch": os.environ.get("MANIM_CACHE_EPOCH", "1"),
                "scope": "Executable bytes and server-interpreter Manim distribution; external configuration, plugins, fonts and assets are not fully captured."}
    if binary and binary.is_file():
        stat = binary.stat()
        identity["executable_bytes"] = stat.st_size
        if stat.st_size <= 64 * 1024 * 1024:
            identity["executable_sha256"] = _sha256_file(binary)
        else:
            identity["executable_mtime_ns"] = stat.st_mtime_ns
            identity["scope"] += " Large executable uses size/mtime, not a full digest."
    return identity


def _render_id(code: str, scene_name: str, quality: str, engine: Optional[dict] = None) -> str:
    payload = {"code_sha256": hashlib.sha256(code.encode()).hexdigest(),
               "scene_name": scene_name, "quality": quality,
               "engine": _engine_identity() if engine is None else engine}
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:24]
    return f"{scene_name}_{quality}_{digest}"


def _artifact_path(render_id: str, extension: str) -> Path:
    if not isinstance(render_id, str) or not _RENDER_ID.fullmatch(render_id):
        raise ValueError("Invalid render_id")
    if extension not in {".mp4", ".png", ".json"}:
        raise ValueError("Invalid artifact extension")
    path = OUTPUT_DIR / (render_id + extension)
    if path.is_symlink() or path.resolve().parent != OUTPUT_DIR:
        raise ValueError("Artifact path escapes output directory or is a symlink")
    return path


def _find_output_video(search_root: Path, scene_name: str = "") -> Optional[Path]:
    videos = sorted(p for p in search_root.rglob("*.mp4")
                    if "partial_movie_files" not in p.parts and p.is_file() and p.stat().st_size > 0)
    if scene_name:
        return next((p for p in videos if p.stem == scene_name), None)
    return videos[0] if videos else None


def _read_metadata(render_id: str) -> dict:
    path = _artifact_path(render_id, ".json")
    try:
        if path.stat().st_size > 64 * 1024:
            return {}
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


def _atomic_copy(source: Path, target: Path) -> None:
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=OUTPUT_DIR, prefix=".publish-", suffix=target.suffix, delete=False) as handle:
            temporary = Path(handle.name)
            with source.open("rb") as stream:
                shutil.copyfileobj(stream, handle)
        os.replace(temporary, target)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _maybe_encode(path: Path) -> Optional[str]:
    if not path.is_file() or path.is_symlink():
        return None
    size = path.stat().st_size
    if size > MAX_BASE64_BYTES:
        log.warning("File %s is %.1f MB — too large to embed as base64", path, size / 1e6)
        return None
    return base64.b64encode(path.read_bytes()).decode("ascii")


def _extract_preview_frame(video_path: Path, out_path: Path) -> bool:
    """Extract a bounded final-frame preview and publish it atomically."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=OUTPUT_DIR, prefix=".preview-", suffix=".png", delete=False) as handle:
            temporary = Path(handle.name)
        result = subprocess.run(
            ["ffmpeg", "-y", "-sseof", "-0.1", "-i", str(video_path),
             "-frames:v", "1", "-q:v", "2", str(temporary)],
            capture_output=True, timeout=15)
        if result.returncode != 0 or not temporary.is_file() or temporary.stat().st_size == 0:
            return False
        os.replace(temporary, out_path)
        return True
    except Exception as error:
        log.warning("Preview extraction failed: %s", error)
        return False
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _write_sidecar_json(
    rid: str,
    scene_name: str,
    quality: str,
    duration: float,
    code: str,
    engine: dict,
    video_sha256: str,
) -> None:
    """Metadata is the final cache commit marker after atomic video publication."""
    sidecar = _artifact_path(rid, ".json")
    payload = {
        "render_id": rid,
        "scene_name": scene_name,
        "quality": quality,
        "rendered_at": datetime.now(timezone.utc).isoformat(),
        "duration_seconds": round(duration, 2),
        "code_sha256": hashlib.sha256(code.encode()).hexdigest(),
        "engine": engine,
        "video_sha256": video_sha256,
        "cache_schema": 2,
    }
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=OUTPUT_DIR, prefix=".metadata-", suffix=".json", delete=False) as handle:
        temporary = Path(handle.name)
        json.dump(payload, handle, indent=2)
    try:
        os.replace(temporary, sidecar)
    finally:
        temporary.unlink(missing_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
# Core render engine
# ══════════════════════════════════════════════════════════════════════════════

async def _bounded_output(stream, limit: int = 128 * 1024) -> bytes:
    tail = bytearray()
    while True:
        block = await stream.read(16384)
        if not block:
            return bytes(tail)
        tail.extend(block)
        if len(tail) > limit:
            del tail[:-limit]


async def _stop_process(proc) -> None:
    # On POSIX the process session also owns Manim's ffmpeg descendants.
    if os.name == "posix":
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except (ProcessLookupError, AttributeError, PermissionError):
            if proc.returncode is None:
                try:
                    proc.kill()
                except ProcessLookupError:
                    pass
    elif proc.returncode is None:
        proc.kill()
    await proc.wait()


async def _run_manim(script_path: Path, scene_name: str, quality: str,
                     work_dir: Path) -> tuple[bool, str, Optional[Path], bool]:
    cmd = [MANIM_EXECUTABLE, *QUALITY_FLAGS[quality], "--format", "mp4",
           "--media_dir", str(work_dir / "media"), "--output_file", scene_name,
           str(script_path), scene_name]
    log.info("Rendering trusted local scene %s at %s", scene_name, quality)
    readers = []
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
            cwd=str(work_dir), start_new_session=os.name == "posix")
        readers = [asyncio.create_task(_bounded_output(proc.stdout)),
                   asyncio.create_task(_bounded_output(proc.stderr))]
        await asyncio.wait_for(proc.wait(), timeout=RENDER_TIMEOUT)
        stdout, stderr = await asyncio.wait_for(asyncio.gather(*readers), timeout=5)
    except asyncio.TimeoutError:
        await _stop_process(proc)
        for reader in readers:
            reader.cancel()
        await asyncio.gather(*readers, return_exceptions=True)
        return False, f"Render timed out after {RENDER_TIMEOUT}s or failed to close its output pipes", None, True
    except asyncio.CancelledError:
        if "proc" in locals():
            await _stop_process(proc)
        for reader in readers:
            reader.cancel()
        await asyncio.gather(*readers, return_exceptions=True)
        raise
    except FileNotFoundError:
        return False, f"Manim executable not found: {MANIM_EXECUTABLE!r}", None, False
    combined = (stderr + stdout).decode(errors="replace")
    if proc.returncode != 0:
        return False, combined, None, False
    video = _find_output_video(work_dir / "media", scene_name)
    if video is None:
        return False, "Manim exited 0 but no nonempty final MP4 for this scene was found.\n" + combined, None, False
    return True, combined, video, False


async def _render_one(code: str, scene_name: str, quality: str,
                      return_base64: bool = True) -> dict:
    if not _validate_identifier(scene_name):
        return {"success": False, "error": "Invalid scene_name; use a Python identifier of at most 128 characters."}
    if not isinstance(quality, str) or quality not in QUALITY_FLAGS:
        return {"success": False, "error": "Unknown quality preset."}
    if not isinstance(code, str) or len(code.encode()) > MAX_CODE_BYTES:
        return {"success": False, "error": "Code must be text within the 256 KiB input budget."}
    try:
        ast.parse(code)
    except (SyntaxError, ValueError) as error:
        return {"success": False, "error": "Invalid Python syntax: " + str(error)}
    engine = await asyncio.to_thread(_engine_identity)
    rid = _render_id(code, scene_name, quality, engine)
    lock = _RENDER_LOCKS.get(rid)
    if lock is None:
        lock = asyncio.Lock()
        _RENDER_LOCKS[rid] = lock
    async with lock:
        # Every single/batch request shares this process-wide render budget.
        async with _GLOBAL_RENDER_SEMAPHORE:
            _ACTIVE_RENDERS.add(rid)
            try:
                return await _render_locked(code, scene_name, quality, return_base64, engine, rid)
            finally:
                _ACTIVE_RENDERS.discard(rid)


async def _render_locked(code, scene_name, quality, return_base64, engine, rid) -> dict:
    start = time.perf_counter()
    final_mp4 = _artifact_path(rid, ".mp4")
    final_png = _artifact_path(rid, ".png")
    meta = _read_metadata(rid)
    valid = final_mp4.is_file() and meta.get("cache_schema") == 2 and meta.get("engine") == engine
    if valid:
        valid = meta.get("video_sha256") == await asyncio.to_thread(_sha256_file, final_mp4)
    if valid:
        if EXTRACT_PREVIEW and not final_png.exists():
            await asyncio.to_thread(_extract_preview_frame, final_mp4, final_png)
        return await _render_result(rid, scene_name, quality, start, True, "(cached)", return_base64, engine)
    with tempfile.TemporaryDirectory(prefix="manim_mcp_") as temporary:
        work = Path(temporary)
        script = work / "scene.py"
        script.write_text(code, encoding="utf-8")
        success, output, video, timed_out = await _run_manim(script, scene_name, quality, work)
        if not success:
            return {"success": False, "error": output[-3000:], "scene_name": scene_name,
                    "quality": quality, "diagnostics": DiagnosticsEngine.parse(output, timed_out),
                    "duration_seconds": round(time.perf_counter() - start, 2)}
        await asyncio.to_thread(_atomic_copy, video, final_mp4)
    if EXTRACT_PREVIEW:
        # ffmpeg's bounded subprocess runs off the MCP event loop.
        await asyncio.to_thread(_extract_preview_frame, final_mp4, final_png)
    digest = await asyncio.to_thread(_sha256_file, final_mp4)
    _write_sidecar_json(rid, scene_name, quality, time.perf_counter() - start, code, engine, digest)
    return await _render_result(rid, scene_name, quality, start, False, output[-3000:], return_base64, engine)


async def _render_result(rid, scene_name, quality, start, cached, output, return_base64, engine):
    result = {"success": True, "video_path": str(_artifact_path(rid, ".mp4")),
              "render_id": rid, "duration_seconds": round(time.perf_counter() - start, 2),
              "quality": quality, "scene_name": scene_name, "cached": cached,
              "manim_output": output, "diagnostics": [], "engine": engine}
    if return_base64 and RETURN_BASE64:
        result["base64_video"] = await asyncio.to_thread(_maybe_encode, _artifact_path(rid, ".mp4"))
    if EXTRACT_PREVIEW:
        result["preview_frame"] = await asyncio.to_thread(_maybe_encode, _artifact_path(rid, ".png"))
    return result


# ══════════════════════════════════════════════════════════════════════════════
# Tool: render_manim
# ══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
async def render_manim(
    code: str,
    scene_name: str = "",
    quality: Literal["low", "medium", "high", "production"] = "medium",
    return_base64: bool = True,
) -> dict:
    """
    Render a Manim animation scene from Python source code into an MP4 video.

    Provide a complete, self-contained Manim script. The server auto-detects the
    Scene class if scene_name is not specified.

    Args:
        code: Complete Manim Python script with all imports and at least one Scene subclass.
        scene_name: Exact class name of the Scene to render. Auto-detected if omitted.
        quality: 'low' (480p/15fps), 'medium' (720p/30fps), 'high' (1080p/60fps),
                 'production' (4K/60fps). Use 'low' for iteration.
        return_base64: Embed MP4 bytes as base64 in the response (capped at 20 MB).

    Returns:
        success, video_path, render_id, duration_seconds, quality, scene_name,
        cached, manim_output, diagnostics (structured errors), preview_frame (PNG),
        base64_video (if requested).
    """
    # Auto-detect scene
    detected = _extract_scene_names(code)
    if not scene_name:
        if not detected:
            return {
                "success": False,
                "error": (
                    "No Scene subclass found in code. "
                    "Add a class inheriting from Scene with a construct() method."
                ),
                "diagnostics": [],
            }
        scene_name = detected[0]
        log.info("Auto-detected scene: %s", scene_name)

    return await _render_one(code, scene_name, quality, return_base64)


# ══════════════════════════════════════════════════════════════════════════════
# Tool: render_manim_batch (v2.0)
# ══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
async def render_manim_batch(
    code: str,
    scene_names: list[str] | None = None,
    quality: Literal["low", "medium", "high", "production"] = "medium",
    max_parallel: int = 2,
) -> dict:
    """
    Render multiple Manim scenes from the same script in a single call.

    Reduces round-trips for scripts with multiple Scene classes. Renders run
    concurrently up to max_parallel (capped at 4). Each scene is independently
    cached — already-rendered scenes are skipped automatically.

    Args:
        code: Manim Python script defining one or more Scene classes.
        scene_names: Which scenes to render. If empty/None, renders ALL detected scenes.
        quality: Applied uniformly to all scenes.
        max_parallel: Max concurrent renders (1–4).

    Returns:
        total, succeeded, failed, results (list of per-scene render results).
    """
    detected = _extract_scene_names(code)
    targets = scene_names if scene_names else detected

    if not targets:
        return {
            "total": 0,
            "succeeded": 0,
            "failed": 0,
            "results": [],
            "error": "No scenes found in code and no scene_names provided.",
        }

    if isinstance(max_parallel, bool) or not isinstance(max_parallel, int) or not 1 <= max_parallel <= 4:
        return {"total": 0, "succeeded": 0, "failed": 0, "results": [], "error": "max_parallel must be an integer in 1..4."}
    if not isinstance(targets, list) or len(targets) > MAX_BATCH_SCENES:
        return {"total": 0, "succeeded": 0, "failed": 0, "results": [], "error": "A batch may contain at most sixteen scenes."}
    sem = asyncio.Semaphore(min(MAX_PARALLEL, max_parallel))

    async def _guarded(sn: str) -> dict:
        async with sem:
            return await _render_one(code, sn, quality, return_base64=False)

    results = await asyncio.gather(*[_guarded(sn) for sn in targets])

    succeeded = sum(1 for r in results if r.get("success"))
    return {
        "total": len(results),
        "succeeded": succeeded,
        "failed": len(results) - succeeded,
        "results": list(results),
    }


# ══════════════════════════════════════════════════════════════════════════════
# Tool: validate_manim_code
# ══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
async def validate_manim_code(code: str) -> dict:
    """
    Statically validate Manim Python code without rendering (returns in <100ms).

    Catches syntax errors, missing imports, missing Scene classes, deprecated
    API usage, ghost objects, and common runtime mistakes before a slow render.

    Args:
        code: Manim Python source to validate.

    Returns:
        valid (bool), errors, warnings, suggestions, detected_scenes.
    """
    errors: list[str] = []
    warnings: list[str] = []
    suggestions: list[str] = []

    warnings.append("Diagnostic checks only: rendering executes Python with host privileges; this validator is not a sandbox.")
    if not isinstance(code, str) or len(code.encode()) > MAX_CODE_BYTES:
        return {"valid": False, "errors": ["Code exceeds the 256 KiB text input budget."], "warnings": warnings, "suggestions": [], "detected_scenes": []}
    # 1. Syntax check
    try:
        compile(code, "<manim_code>", "exec")
    except SyntaxError as e:
        return {
            "valid": False,
            "errors": [f"SyntaxError at line {e.lineno}: {e.msg}"],
            "warnings": [],
            "suggestions": [],
            "detected_scenes": [],
        }

    # 2. Manim import
    if "from manim import" not in code and "import manim" not in code:
        warnings.append("No Manim import detected. Add 'from manim import *' at the top.")

    # 3. Scene class
    scenes = _extract_scene_names(code)
    if not scenes:
        errors.append(
            "No Scene subclass found. Define a class inheriting from Scene "
            "(e.g. 'class MyScene(Scene):')."
        )

    # 4. construct() method
    if "def construct(self" not in code:
        errors.append(
            "No construct(self) method found. Manim requires each Scene to "
            "implement 'def construct(self): ...'."
        )

    # 5. Empty self.play()
    if "self.play()" in code:
        errors.append(
            "Empty self.play() call — Manim requires at least one animation argument."
        )

    # 6. self.add without self.play (static-only)
    if "self.add(" in code and "self.play(" not in code:
        warnings.append(
            "Using self.add() without self.play() — scene may render as a static image."
        )

    # 7. self.wait(0) no-op
    if re.search(r"self\.wait\(\s*0\s*\)", code):
        warnings.append("self.wait(0) is a no-op. Remove it or use self.wait(0.1) for a brief pause.")

    # 8. Deprecated APIs
    deprecated = {
        "ShowCreation": "Create",
        "FadeInFrom": "FadeIn(shift=...)",
        "ApplyMethod": ".animate syntax (e.g. obj.animate.shift(UP))",
        "GrowFromCenter": "Create or GrowFromEdge",
    }
    for old, new in deprecated.items():
        if old in code:
            warnings.append(f"Deprecated: '{old}' — use '{new}' instead.")

    # 9. ThreeDScene hint
    if "ThreeDScene" in code:
        suggestions.append("ThreeDScene can use Cairo or OpenGL. Select and measure the backend in your actual environment; 3D does not itself require OpenGL.")

    # 10. Ghost objects heuristic (assigned but never used in add/play)
    assigned = set(re.findall(r"(\w+)\s*=\s*(?:MathTex|Tex|Text|Circle|Square|Arrow|Line|Dot|"
                               r"Rectangle|Polygon|Triangle|VGroup|Group)\s*\(", code))
    used_in_play = set(re.findall(r"self\.(?:play|add)\s*\(([^)]*)\)", code))
    used_flat = set(w for block in used_in_play for w in re.findall(r"\b(\w+)\b", block))
    ghosts = assigned - used_flat
    if ghosts:
        warnings.append(
            f"Possible ghost objects (created but never added/played): "
            f"{', '.join(sorted(ghosts))}. This heuristic can miss composition and indirect use."
        )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "suggestions": suggestions,
        "detected_scenes": scenes,
    }


# ══════════════════════════════════════════════════════════════════════════════
# Tool: suggest_quality (v2.0)
# ══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
async def suggest_quality(
    code: str,
    intended_use: Literal["iteration", "review", "sharing", "publication"] = "iteration",
) -> dict:
    """
    Recommend a render quality level based on code complexity and intended use.

    Analyzes the script and returns a recommendation with rough time estimates,
    so you can avoid accidentally starting a 20-minute production render.

    Args:
        code: Manim Python source to analyze.
        intended_use: 'iteration' (fast), 'review', 'sharing', 'publication' (final).

    Returns:
        recommended_quality, estimated_render_seconds (per quality level),
        reasoning, complexity_score (1–10).
    """
    if not isinstance(code, str) or len(code.encode()) > MAX_CODE_BYTES:
        return {"error": "Code exceeds the 256 KiB text input budget."}
    if intended_use not in {"iteration", "review", "sharing", "publication"}:
        return {"error": "Unknown intended_use."}
    # Complexity scoring
    play_calls = len(re.findall(r"self\.play\(", code))
    mathtex_count = len(re.findall(r"(?:MathTex|Tex)\s*\(", code))
    has_3d = "ThreeDScene" in code
    has_tracker = "ValueTracker" in code and "always_redraw" in code
    line_count = code.count("\n") + 1

    score = (
        play_calls * 1
        + mathtex_count * 2
        + (3 if has_3d else 0)
        + (2 if has_tracker else 0)
        + math.log2(max(line_count, 1))
    )
    score = max(1, min(10, round(score)))

    # Base seconds estimate at 'low' quality = score * 2
    base_low = score * 2
    estimates = {
        "low":        round(base_low),
        "medium":     round(base_low * 4),
        "high":       round(base_low * 10),
        "production": round(base_low * 40),
    }

    # Recommended quality
    use_boost = {"iteration": 0, "review": 1, "sharing": 1, "publication": 2}
    boosted_score = score + use_boost.get(intended_use, 0)

    if intended_use == "publication":
        recommended = "high" if score <= 6 else "production"
    elif boosted_score <= 4:
        recommended = "low"
    elif boosted_score <= 7:
        recommended = "medium"
    elif boosted_score <= 9:
        recommended = "high"
    else:
        recommended = "low"  # Very complex → start low, iterate

    reasons = []
    if play_calls:
        reasons.append(f"{play_calls} self.play() call(s)")
    if mathtex_count:
        reasons.append(f"{mathtex_count} LaTeX object(s) (slow to compile)")
    if has_3d:
        reasons.append("ThreeDScene (+3 complexity)")
    if has_tracker:
        reasons.append("ValueTracker + always_redraw (+2 complexity)")
    reasons.append(f"{line_count} lines of code")

    reasoning = (
        f"Complexity score {score}/10 based on: {', '.join(reasons)}. "
        f"Intended use '{intended_use}' → recommended '{recommended}'. "
        f"Estimated render time at low: ~{estimates['low']}s, "
        f"medium: ~{estimates['medium']}s, "
        f"high: ~{estimates['high']}s."
    )
    if score > 8 and intended_use != "publication":
        reasoning += " Score >8: consider starting with 'low' for fast iteration."

    return {
        "recommended_quality": recommended,
        "estimated_render_seconds": estimates,
        "reasoning": reasoning,
        "complexity_score": score,
        "estimate_scope": "Uncalibrated source heuristic, not a measured render-time prediction.",
    }


# ══════════════════════════════════════════════════════════════════════════════
# Tool: list_renders
# ══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
async def list_renders(filter_scene: str = "") -> dict:
    """
    List all previously rendered Manim videos on disk.

    Args:
        filter_scene: If provided, return only renders whose render_id contains
                      this string (typically the scene class name).

    Returns:
        render_count, output_dir, renders (list of metadata per file).
    """
    renders = []
    for p in sorted((p for p in OUTPUT_DIR.glob("*.mp4") if _RENDER_ID.fullmatch(p.stem) and p.stem not in _ACTIVE_RENDERS and not p.is_symlink()), key=lambda f: f.stat().st_mtime, reverse=True):
        if filter_scene and filter_scene not in p.stem:
            continue
        stat = p.stat()
        # Load sidecar JSON if available
        meta: dict = {}
        try:
            meta = _read_metadata(p.stem)
        except ValueError:
            continue
        renders.append({
            "render_id": p.stem,
            "filename": p.name,
            "path": str(p),
            "size_mb": round(stat.st_size / 1e6, 2),
            "modified": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime)),
            "scene_name": meta.get("scene_name"),
            "quality": meta.get("quality"),
            "rendered_at": meta.get("rendered_at"),
            "has_preview": (OUTPUT_DIR / f"{p.stem}.png").exists(),
        })
    return {
        "render_count": len(renders),
        "output_dir": str(OUTPUT_DIR),
        "renders": renders,
    }


# ══════════════════════════════════════════════════════════════════════════════
# Tool: get_render_info
# ══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
async def get_render_info(render_id: str, include_base64: bool = False) -> dict:
    """Read one local artifact; identifiers cannot contain paths."""
    try:
        mp4 = _artifact_path(render_id, ".mp4")
        png = _artifact_path(render_id, ".png")
        meta = _read_metadata(render_id)
    except ValueError as error:
        return {"found": False, "error": str(error)}
    if render_id in _ACTIVE_RENDERS:
        return {"found": False, "render_id": render_id, "pending": True}
    if not mp4.is_file():
        return {"found": False, "render_id": render_id}
    if include_base64 and not png.exists() and render_id not in _ACTIVE_RENDERS:
        await asyncio.to_thread(_extract_preview_frame, mp4, png)
    result = {"found": True, "render_id": render_id, "path": str(mp4),
              "size_mb": round(mp4.stat().st_size / 1e6, 2), "metadata": meta,
              "scene_name": meta.get("scene_name"), "quality": meta.get("quality")}
    if include_base64:
        result["base64_video"] = await asyncio.to_thread(_maybe_encode, mp4)
        result["preview_frame"] = await asyncio.to_thread(_maybe_encode, png)
    return result


# ══════════════════════════════════════════════════════════════════════════════
# Tool: cleanup_renders
# ══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
async def cleanup_renders(keep_latest: int = 10) -> dict:
    """
    Delete old render files, keeping only the most recent N renders.

    Also removes associated .png preview and .json sidecar files.

    Args:
        keep_latest: Number of most-recent renders to keep (default 10). 0 = delete all.

    Returns:
        deleted_count, freed_mb, kept_count, deleted_files.
    """
    if isinstance(keep_latest, bool) or not isinstance(keep_latest, int) or not 0 <= keep_latest <= 10000:
        return {"deleted_count": 0, "error": "keep_latest must be an integer in 0..10000."}
    all_renders = sorted(
        (p for p in OUTPUT_DIR.glob("*.mp4") if _RENDER_ID.fullmatch(p.stem) and not p.is_symlink()),
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )
    to_delete = all_renders[keep_latest:]
    freed_bytes = 0
    deleted: list[str] = []

    for p in to_delete:
        if p.stem in _ACTIVE_RENDERS:
            continue
        freed_bytes += p.stat().st_size
        p.unlink()
        deleted.append(p.name)
        # Also delete sidecars
        for ext in (".png", ".json"):
            sidecar = p.with_suffix(ext)
            if sidecar.is_file() and not sidecar.is_symlink():
                freed_bytes += sidecar.stat().st_size
                sidecar.unlink()

    return {
        "deleted_count": len(deleted),
        "freed_mb": round(freed_bytes / 1e6, 2),
        "kept_count": len(all_renders) - len(deleted),
        "deleted_files": deleted,
    }


# ══════════════════════════════════════════════════════════════════════════════
# Entry point
# ══════════════════════════════════════════════════════════════════════════════

def main():
    """Entry point for 'uvx manim-mcp' and direct python invocation."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
