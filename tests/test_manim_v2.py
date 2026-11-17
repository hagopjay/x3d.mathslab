"""Direct tests of the v2.1 source with an explicit MCP registration adapter.

No Manim scene is rendered by these controls. Render payloads are test bytes;
process lifecycle additionally exercises one owned Python child, not Manim.
"""
import asyncio
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import time
import types
import unittest
from unittest.mock import AsyncMock, patch

SOURCE = Path(__file__).resolve().parents[1] / 'src/manim_mcp/server.py'
CODE = 'from manim import *\nclass Demo(Scene):\n    def construct(self):\n        self.wait(.1)\n'


def load_server(output, **extra):
    class RegistrationAdapter:
        def __init__(self, *args, **kwargs):
            self.instructions = kwargs.get('instructions', '')
        def tool(self):
            return lambda function: function
    modules = {name: types.ModuleType(name) for name in ('mcp', 'mcp.server', 'mcp.server.fastmcp')}
    modules['mcp.server.fastmcp'].FastMCP = RegistrationAdapter
    env = {'MANIM_OUTPUT_DIR': str(output), 'MANIM_PREVIEW_FRAME': '0',
           'MANIM_RETURN_BASE64': '0', 'MANIM_TIMEOUT': '120', 'MANIM_MAX_PARALLEL': '2',
           'MANIM_MAX_BASE64_BYTES': '1024', **extra}
    spec = importlib.util.spec_from_file_location('tested_manim_server', SOURCE)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, modules), patch.dict(os.environ, env):
        spec.loader.exec_module(module)
    return module


class ManimTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='mathlab-manim-test-')
        self.root = Path(self.temp.name)
        self.s = load_server(self.root)
        self.identity = patch.object(self.s, '_engine_identity', return_value={'engine': 'instrumented-test'})
        self.identity.start()
        self.calls = 0
        self.active = 0
        self.peak = 0

    def tearDown(self):
        self.identity.stop()
        self.temp.cleanup()

    async def fake_render(self, script, scene, quality, work):
        self.calls += 1
        self.active += 1
        self.peak = max(self.peak, self.active)
        try:
            await asyncio.sleep(.025)
            video = work / 'media' / (scene + '.mp4')
            video.parent.mkdir(parents=True)
            video.write_bytes(b'instrumented bytes, not an actual Manim video')
            return True, 'instrumented successful subprocess', video, False
        finally:
            self.active -= 1

    def artifact(self, scene='Demo'):
        rid = self.s._render_id(CODE, scene, 'low', {'engine': 'instrumented-test'})
        return rid, self.root / (rid + '.mp4')

    def test_ast_discovery_ignores_comment_and_string_decoys(self):
        source = '# class Fake(Scene):\ntext="class Other(Scene):"\nimport manim as mn\nclass Child(Parent): pass\nclass Parent(mn.ThreeDScene): pass\nclass Foreign(unrelated.Scene): pass\n'
        self.assertEqual(self.s._extract_scene_names(source), ['Child', 'Parent'])
        alias = 'from manim import Scene as S\nclass Real(S): pass\n'
        self.assertEqual(self.s._extract_scene_names(alias), ['Real'])

    def test_identifiers_and_engine_context_change_identity(self):
        for invalid in ('Demo\n', '../Demo', '/tmp/a', '', 'a' * 129):
            self.assertFalse(self.s._validate_identifier(invalid))
        self.assertTrue(self.s._validate_identifier('_Demo2'))
        first = self.s._render_id(CODE, 'Demo', 'low', {'engine': 'a'})
        self.assertEqual(first, self.s._render_id(CODE, 'Demo', 'low', {'engine': 'a'}))
        self.assertNotEqual(first, self.s._render_id(CODE, 'Demo', 'low', {'engine': 'b'}))
        self.assertNotEqual(first, self.s._render_id(CODE + '\n', 'Demo', 'low', {'engine': 'a'}))

    def test_invalid_environment_is_refused(self):
        for config in ({'MANIM_TIMEOUT': 'NaN'}, {'MANIM_MAX_PARALLEL': '0'},
                       {'MANIM_MAX_BASE64_BYTES': '-1'}):
            with self.assertRaises(ValueError):
                load_server(self.root, **config)

    async def test_input_limits_refuse_before_rendering(self):
        with patch.object(self.s, '_run_manim', new=AsyncMock()) as run:
            for code, scene, quality in ((CODE, '../x', 'low'), (CODE, 'Demo', 'bogus'),
                                         (CODE, 'Demo', []), ('x' * (256 * 1024 + 1), 'Demo', 'low')):
                result = await self.s._render_one(code, scene, quality, False)
                self.assertFalse(result['success'])
            run.assert_not_awaited()

    async def test_same_id_concurrent_requests_render_once(self):
        with patch.object(self.s, '_run_manim', side_effect=self.fake_render):
            result = await asyncio.gather(*(self.s._render_one(CODE, 'Demo', 'low', False) for _ in range(6)))
        self.assertEqual(self.calls, 1)
        self.assertEqual(sum(not row['cached'] for row in result), 1)
        self.assertTrue(all(row['success'] for row in result))
        self.assertFalse(any(p.name.startswith('.publish-') for p in self.root.iterdir()))

    async def test_single_and_batch_share_global_render_cap(self):
        many = '\n'.join('class ' + name + '(Scene):\n    def construct(self): pass' for name in 'ABCDEFG')
        with patch.object(self.s, '_run_manim', side_effect=self.fake_render):
            jobs = [self.s._render_one(many, name, 'low', False) for name in 'ABC']
            jobs.append(self.s.render_manim_batch(many, list('DEFG'), 'low', 4))
            result = await asyncio.gather(*jobs)
        self.assertEqual(self.calls, 7)
        self.assertLessEqual(self.peak, 2)
        self.assertEqual(result[-1]['succeeded'], 4)

    async def test_cache_requires_commit_metadata_and_matching_video_digest(self):
        with patch.object(self.s, '_run_manim', side_effect=self.fake_render):
            first = await self.s._render_one(CODE, 'Demo', 'low', False)
            cached = await self.s._render_one(CODE, 'Demo', 'low', False)
            self.assertTrue(cached['cached'])
            Path(first['video_path']).write_bytes(b'changed')
            repaired = await self.s._render_one(CODE, 'Demo', 'low', False)
            self.assertFalse(repaired['cached'])
            (self.root / (first['render_id'] + '.json')).unlink()
            no_commit = await self.s._render_one(CODE, 'Demo', 'low', False)
            self.assertFalse(no_commit['cached'])
        self.assertEqual(self.calls, 3)

    def test_final_video_selection_ignores_partial_and_other_scene(self):
        partial = self.root / 'partial_movie_files' / 'Demo' / 'a.mp4'
        partial.parent.mkdir(parents=True)
        partial.write_bytes(b'partial')
        (self.root / 'Other.mp4').write_bytes(b'other')
        self.assertIsNone(self.s._find_output_video(self.root, 'Demo'))
        final = self.root / 'Demo.mp4'
        final.write_bytes(b'final')
        self.assertEqual(self.s._find_output_video(self.root, 'Demo'), final)

    async def test_preview_work_does_not_stall_event_loop(self):
        self.s.EXTRACT_PREVIEW = True
        def slow_preview(video, target):
            time.sleep(.1)
            target.write_bytes(b'instrumented png')
            return True
        ticks = 0
        async def pulse():
            nonlocal ticks
            for _ in range(12):
                await asyncio.sleep(.01)
                ticks += 1
        with patch.object(self.s, '_run_manim', side_effect=self.fake_render), patch.object(self.s, '_extract_preview_frame', side_effect=slow_preview):
            job = asyncio.create_task(self.s._render_one(CODE, 'Demo', 'low', False))
            await asyncio.sleep(.055)
            self.assertFalse(job.done())
            pulse_job = asyncio.create_task(pulse())
            await job
            self.assertGreaterEqual(ticks, 3)
            await pulse_job

    async def test_timeout_kills_and_awaits_child(self):
        class Process:
            def __init__(self):
                self.pid = 123456789
                self.returncode = None
                self.stdout = asyncio.StreamReader(); self.stdout.feed_eof()
                self.stderr = asyncio.StreamReader(); self.stderr.feed_eof()
                self.done = asyncio.Event(); self.kills = 0; self.waits = 0
            def kill(self):
                self.kills += 1; self.returncode = -9; self.done.set()
            async def wait(self):
                self.waits += 1; await self.done.wait(); return self.returncode
        proc = Process(); self.s.RENDER_TIMEOUT = .01
        with patch.object(self.s.asyncio, 'create_subprocess_exec', new=AsyncMock(return_value=proc)), patch.object(self.s.os, 'killpg', side_effect=ProcessLookupError):
            result = await self.s._run_manim(self.root / 'scene.py', 'Demo', 'low', self.root)
        self.assertFalse(result[0]); self.assertTrue(result[3])
        self.assertEqual(proc.kills, 1); self.assertGreaterEqual(proc.waits, 2)

    async def test_cancellation_also_reaps_child(self):
        class Process:
            pid = 123456789
            returncode = None
            def __init__(self):
                self.stdout = asyncio.StreamReader(); self.stdout.feed_eof()
                self.stderr = asyncio.StreamReader(); self.stderr.feed_eof()
                self.done = asyncio.Event(); self.kills = 0
            def kill(self):
                self.kills += 1; self.returncode = -9; self.done.set()
            async def wait(self):
                await self.done.wait(); return self.returncode
        proc = Process()
        with patch.object(self.s.asyncio, 'create_subprocess_exec', new=AsyncMock(return_value=proc)), patch.object(self.s.os, 'killpg', side_effect=ProcessLookupError):
            task = asyncio.create_task(self.s._run_manim(self.root / 'scene.py', 'Demo', 'low', self.root))
            await asyncio.sleep(.01); task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await task
        self.assertEqual(proc.kills, 1); self.assertIsNotNone(proc.returncode)

    async def test_owned_real_python_child_is_reaped(self):
        proc = await asyncio.create_subprocess_exec(sys.executable, '-c', 'import time; time.sleep(60)',
                    stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL,
                    start_new_session=os.name == 'posix')
        await asyncio.wait_for(self.s._stop_process(proc), timeout=2)
        self.assertIsNotNone(proc.returncode)

    async def test_output_tail_is_bounded_and_small_output_retained(self):
        stream = asyncio.StreamReader()
        stream.feed_data(b'a' * 200000 + b'END'); stream.feed_eof()
        tail = await self.s._bounded_output(stream)
        self.assertEqual(len(tail), 128 * 1024); self.assertTrue(tail.endswith(b'END'))
        small = asyncio.StreamReader(); small.feed_data(b'healthy'); small.feed_eof()
        self.assertEqual(await self.s._bounded_output(small), b'healthy')

    async def test_render_id_paths_and_symlinks_are_refused(self):
        for bad in ('../outside', '/tmp/outside', 'Demo_low_123456789abc/../../outside', 'x\x00y'):
            self.assertFalse((await self.s.get_render_info(bad, True))['found'])
        rid, path = self.artifact()
        outside = self.root / 'outside.txt'; outside.write_text('retained')
        path.symlink_to(outside)
        self.assertFalse((await self.s.get_render_info(rid, True))['found'])
        await self.s.cleanup_renders(0)
        self.assertEqual(outside.read_text(), 'retained')

    async def test_cleanup_negative_and_active_artifacts_are_preserved(self):
        rid, path = self.artifact(); path.write_bytes(b'active')
        other, completed = self.artifact('Other'); completed.write_bytes(b'complete')
        for bad in (-1, True, 1.5):
            result = await self.s.cleanup_renders(bad)
            self.assertEqual(result['deleted_count'], 0)
            self.assertTrue(completed.exists())
        self.s._ACTIVE_RENDERS.add(rid)
        result = await self.s.cleanup_renders(0)
        self.assertEqual(result['deleted_count'], 1)
        self.assertTrue(path.exists()); self.assertFalse(completed.exists())

    async def test_untrusted_sidecar_cannot_override_returned_path(self):
        rid, path = self.artifact(); path.write_bytes(b'video')
        (self.root / (rid + '.json')).write_text('{"path":"/outside","found":false}')
        result = await self.s.get_render_info(rid)
        self.assertTrue(result['found']); self.assertEqual(result['path'], str(path))
        self.assertEqual(result['metadata']['path'], '/outside')

    async def test_batch_limits_and_quality_estimate_scope(self):
        for parallel in (0, 5, True):
            result = await self.s.render_manim_batch(CODE, ['Demo'], 'low', parallel)
            self.assertIn('error', result)
        self.assertIn('error', await self.s.render_manim_batch(CODE, ['Demo'] * 17))
        result = await self.s.suggest_quality(CODE, 'iteration')
        self.assertIn('Uncalibrated', result['estimate_scope'])

    async def test_static_validation_is_explicitly_not_isolation(self):
        result = await self.s.validate_manim_code(CODE)
        self.assertTrue(result['valid'])
        self.assertTrue(any('not a sandbox' in text for text in result['warnings']))
        diag = self.s.DiagnosticsEngine.parse("NameError: name 'missing' is not defined")
        self.assertTrue(any(row['code'] == 'NAME_ERROR' for row in diag))


if __name__ == '__main__':
    unittest.main()
