"""Optional MCP wrapper controls using the installed official SDK for registration.

Transport is exercised separately by tools/probe_math_mcp.py. No Manim runs.
"""
import hashlib
import re
import importlib.util
import sys
import unittest

def ga(obj, camel):
    """Read an MCP model attribute under mcp 1.x camelCase or 2.x snake_case."""
    if hasattr(obj, camel):
        return getattr(obj, camel)
    return getattr(obj, re.sub(r'([A-Z])', lambda m: '_' + m.group(1).lower(), camel))


SDK_AVAILABLE = importlib.util.find_spec('mcp') is not None


@unittest.skipUnless(SDK_AVAILABLE, 'Optional MCP SDK not installed; protocol result is not claimed.')
class MathMCPTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        from mathlab import mcp_server
        self.server = mcp_server

    async def test_catalog_has_six_lessons_and_three_read_only_tools(self):
        result = await self.server.mathlab_list_lessons()
        self.assertEqual({row['id'] for row in result['lessons']},
                         {'linear', 'derivative', 'integral', 'fourier', 'lorenz', 'gradient'})
        tools = await self.server.mcp.list_tools()
        self.assertEqual({tool.name for tool in tools},
                         {'mathlab_list_lessons', 'mathlab_scene', 'mathlab_manim_source'})
        self.assertTrue(all(ga(tool.annotations, "readOnlyHint") for tool in tools))
        self.assertTrue(all(not ga(tool.annotations, "openWorldHint") for tool in tools))

    async def test_scene_identity_matches_actual_returned_bytes(self):
        result = await self.server.mathlab_scene('derivative', {'x': 1, 'h': .1})
        self.assertEqual(result['sample']['lesson'], 'derivative')
        self.assertIn('<X3D', result['x3d'])
        self.assertEqual(result['identity']['x3d_sha256'],
                         hashlib.sha256(result['x3d'].encode()).hexdigest())
        self.assertEqual(result['identity']['sample_sha256'],
                         hashlib.sha256(self.server.canonical(result['sample'])).hexdigest())

    async def test_source_uses_same_identity_without_importing_manim(self):
        before = 'manim' in sys.modules
        scene = await self.server.mathlab_scene('linear')
        result = await self.server.mathlab_manim_source('linear')
        self.assertEqual(result['identity']['sample_sha256'], scene['identity']['sample_sha256'])
        self.assertEqual(result['identity']['x3d_sha256'], scene['identity']['x3d_sha256'])
        self.assertEqual(hashlib.sha256(result['source'].encode()).hexdigest(),
                         result['identity']['manim_source_sha256'])
        compile(result['source'], '<generated-manim-source>', 'exec')
        self.assertEqual('manim' in sys.modules, before)

    async def test_invalid_boolean_nonfinite_unknown_and_budget_inputs_refuse(self):
        for lesson, params in [('derivative', {'x': True}), ('derivative', {'x': float('nan')}),
                               ('derivative', {'x': float('inf')}), ('missing', {}),
                               ('derivative', {'unknown': 2}), ('derivative', {'h': 0}),
                               ('derivative', {str(i): i for i in range(17)}),
                               ('derivative', {'x' * 33: 1})]:
            with self.subTest(lesson=lesson, params=params):
                with self.assertRaises(ValueError):
                    await self.server.mathlab_scene(lesson, params)


if __name__ == '__main__':
    unittest.main()
