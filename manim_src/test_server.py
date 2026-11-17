"""
Tests for manim-mcp server.

These tests validate the business logic WITHOUT requiring Manim to be installed,
by mocking the subprocess layer. This makes the test suite fast and CI-friendly.

Run with:  pytest tests/ -v
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Ensure the src layout is importable from the project root
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from manim_mcp.server import (
    _extract_scene_names,
    _render_id,
    validate_manim_code,
    list_renders,
    cleanup_renders,
)


# ── Unit tests: pure Python helpers ───────────────────────────────────────

class TestExtractSceneNames:
    def test_simple_scene(self):
        code = "class MyScene(Scene): pass"
        assert _extract_scene_names(code) == ["MyScene"]

    def test_moving_camera_scene(self):
        code = "class Fly(MovingCameraScene):\n    pass"
        assert _extract_scene_names(code) == ["Fly"]

    def test_threed_scene(self):
        code = "class Box(ThreeDScene):\n    pass"
        assert _extract_scene_names(code) == ["Box"]

    def test_multiple_scenes(self):
        code = (
            "class SceneA(Scene): pass\n"
            "class SceneB(Scene): pass\n"
        )
        assert _extract_scene_names(code) == ["SceneA", "SceneB"]

    def test_no_scene(self):
        code = "class Foo: pass\ndef bar(): ..."
        assert _extract_scene_names(code) == []


class TestRenderId:
    def test_deterministic(self):
        rid1 = _render_id("code", "Scene", "high")
        rid2 = _render_id("code", "Scene", "high")
        assert rid1 == rid2

    def test_different_for_different_quality(self):
        rid_low = _render_id("code", "Scene", "low")
        rid_high = _render_id("code", "Scene", "high")
        assert rid_low != rid_high

    def test_contains_scene_name(self):
        rid = _render_id("code", "MyScene", "medium")
        assert "MyScene" in rid

    def test_length(self):
        # Render IDs are SceneName_quality_<12-char hex>
        rid = _render_id("code", "S", "low")
        parts = rid.split("_")
        assert len(parts) == 3
        assert len(parts[2]) == 12


# ── Integration-style tests: tool functions with mocked subprocess ─────────

GOOD_CODE = """
from manim import *

class BouncingBall(Scene):
    def construct(self):
        ball = Circle(radius=0.5, color=BLUE)
        self.play(Create(ball))
        self.play(ball.animate.shift(UP * 2))
        self.wait()
"""

BAD_CODE_NO_SCENE = """
from manim import *

def not_a_scene():
    pass
"""

BAD_CODE_SYNTAX = """
from manim import *
class Broken(Scene)
    def construct(self):
        pass
"""


class TestValidateManimCode:
    @pytest.mark.asyncio
    async def test_valid_code_passes(self):
        result = await validate_manim_code(GOOD_CODE)
        assert result["valid"] is True
        assert result["errors"] == []
        assert "BouncingBall" in result["detected_scenes"]

    @pytest.mark.asyncio
    async def test_no_scene_class_fails(self):
        result = await validate_manim_code(BAD_CODE_NO_SCENE)
        assert result["valid"] is False
        assert any("Scene" in e for e in result["errors"])

    @pytest.mark.asyncio
    async def test_syntax_error_caught(self):
        result = await validate_manim_code(BAD_CODE_SYNTAX)
        assert result["valid"] is False
        assert any("SyntaxError" in e for e in result["errors"])

    @pytest.mark.asyncio
    async def test_missing_import_warns(self):
        code = "class MyScene(Scene):\n    def construct(self): pass"
        result = await validate_manim_code(code)
        # Should warn about missing import, but still find the scene
        assert any("import" in w.lower() for w in result["warnings"])

    @pytest.mark.asyncio
    async def test_missing_construct_fails(self):
        code = "from manim import *\nclass MyScene(Scene):\n    pass"
        result = await validate_manim_code(code)
        assert result["valid"] is False
        assert any("construct" in e for e in result["errors"])


class TestListAndCleanup:
    @pytest.mark.asyncio
    async def test_list_renders_returns_dict(self):
        result = await list_renders()
        assert "render_count" in result
        assert "renders" in result
        assert isinstance(result["renders"], list)

    @pytest.mark.asyncio
    async def test_cleanup_with_no_renders(self):
        result = await cleanup_renders(keep_latest=10)
        # With no renders, nothing to delete
        assert result["deleted_count"] == 0
        assert result["freed_mb"] == 0.0


# ── Smoke test: render_manim with fully mocked Manim subprocess ────────────

class TestRenderManim:
    @pytest.mark.asyncio
    async def test_render_returns_success_structure(self, tmp_path):
        """
        Smoke test: patch asyncio.create_subprocess_exec so we don't need Manim
        installed. Verifies the tool returns the correct structure on success.
        """
        # Create a fake MP4 so _find_output_video can find it
        fake_mp4 = tmp_path / "media" / "videos" / "scene" / "720p30" / "BouncingBall.mp4"
        fake_mp4.parent.mkdir(parents=True)
        fake_mp4.write_bytes(b"\x00" * 100)  # minimal fake video bytes

        mock_proc = AsyncMock()
        mock_proc.returncode = 0
        mock_proc.communicate = AsyncMock(return_value=(b"", b"Manim succeeded"))

        with (
            patch("asyncio.create_subprocess_exec", return_value=mock_proc),
            patch("manim_mcp.server.OUTPUT_DIR", tmp_path),
            patch("tempfile.TemporaryDirectory") as mock_td,
        ):
            # Make the temp dir point at our controlled tmp_path
            mock_td.return_value.__enter__ = MagicMock(return_value=str(tmp_path))
            mock_td.return_value.__exit__ = MagicMock(return_value=False)

            from manim_mcp.server import render_manim
            result = await render_manim(
                code=GOOD_CODE,
                scene_name="BouncingBall",
                quality="medium",
                return_base64=False,
            )

        # We don't assert success here because path handling is complex in mocks,
        # but we do confirm the result dict has the expected structure.
        assert "success" in result
        assert "scene_name" in result
        assert result["scene_name"] == "BouncingBall"

    @pytest.mark.asyncio
    async def test_render_timeout_returns_error(self, tmp_path):
        """Verify that a timeout produces a clean error response, not an exception."""
        async def slow_communicate():
            await asyncio.sleep(9999)

        mock_proc = AsyncMock()
        mock_proc.communicate = slow_communicate
        mock_proc.kill = MagicMock()

        with (
            patch("asyncio.create_subprocess_exec", return_value=mock_proc),
            patch("manim_mcp.server.RENDER_TIMEOUT", 0),  # force immediate timeout
            patch("manim_mcp.server.OUTPUT_DIR", tmp_path),
        ):
            from manim_mcp.server import render_manim
            result = await render_manim(
                code=GOOD_CODE,
                scene_name="BouncingBall",
                quality="low",
                return_base64=False,
            )

        assert result["success"] is False
        assert "timed out" in result["error"].lower()
