"""Baked-data/code-generation controls; no Manim installation or render implied."""

import ast
import copy
import hashlib
import json
import unittest
import xml.etree.ElementTree as ET

from mathlab.manim_bridge import generate_manim


def example():
    return {
        "schema": "mathlab.sample/1", "lesson": "linear", "title": "One shared model",
        "params": {"blend": .5}, "metrics": [], "insights": [],
        "bounds": {"center": [0, 0, 0], "size": [4, 4, 1]},
        "primitives": [
            {"kind": "line", "id": "curve", "points": [[-1, 0, 0], [1, 2, 0]],
             "color": [.2, .8, 1]},
            {"kind": "sphere", "id": "marker", "position": [1, 2, 0],
             "radius": .1, "color": [1, .7, .3]},
            {"kind": "box", "id": "cell", "position": [0, -.5, 0],
             "size": [1, .5, .1], "color": [.4, .9, .6], "transparency": .3},
            {"kind": "mesh", "id": "surface", "points": [[0, 0, 0], [1, 0, 0], [0, 1, 0]],
             "indices": [0, 1, 2, -1], "color": [.7, .5, 1]},
        ],
    }


def literal(source, name):
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError("Missing literal " + name)


class BridgeControls(unittest.TestCase):
    def test_complete_source_compiles_without_importing_manim(self):
        source = generate_manim(example())
        compile(source, "baked_lesson.py", "exec")
        classes = [n for n in ast.parse(source).body if isinstance(n, ast.ClassDef)]
        self.assertEqual([c.name for c in classes], ["MathlabScene"])
        self.assertEqual(classes[0].bases[0].id, "ThreeDScene")

    def test_exact_data_is_retained_with_digest(self):
        sample = example()
        source = generate_manim(sample)
        payload = literal(source, "SAMPLE_JSON")
        self.assertEqual(json.loads(payload), sample)
        self.assertEqual(literal(source, "SAMPLE_SHA256"), hashlib.sha256(payload.encode()).hexdigest())

    def test_deterministic_output_ignores_dictionary_insertion_order(self):
        sample = example()
        reversed_sample = dict(reversed(list(sample.items())))
        self.assertEqual(generate_manim(sample), generate_manim(reversed_sample))

    def test_export_does_not_mutate_input(self):
        sample = example()
        before = copy.deepcopy(sample)
        generate_manim(sample)
        self.assertEqual(sample, before)

    def test_unicode_sample_identity_matches_native_x3d(self):
        from mathlab.x3d import to_x3d
        sample = example()
        sample["title"] = "Rotation θ and Δx"
        metadata = ET.fromstring(to_x3d(sample)).find("Scene/WorldInfo/MetadataString")
        record = json.loads(json.loads(metadata.attrib["value"]))
        source = generate_manim(sample)
        self.assertEqual(literal(source, "SAMPLE_SHA256"), record["sample_sha256"])

    def test_shared_default_color_is_supported_without_altering_source_data(self):
        sample = example()
        del sample["primitives"][0]["color"]
        baked = json.loads(literal(generate_manim(sample), "SAMPLE_JSON"))
        self.assertEqual(baked, sample)

    def test_text_cannot_add_python_statements_or_rewrite_markers(self):
        sample = example()
        sample["title"] = "Quote '\"\n__DIGEST__ __BAKED_LITERAL__\n__import__('os').system('BAD')"
        source = generate_manim(sample)
        self.assertEqual(json.loads(literal(source, "SAMPLE_JSON")), sample)
        tree = ast.parse(source)
        direct = [n.func.id for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)]
        self.assertFalse(set(direct) & {"eval", "exec", "compile", "__import__"})

    def test_no_nan_in_geometry(self):
        sample = example()
        sample["primitives"][0]["points"][0][0] = float("nan")
        with self.assertRaises(ValueError):
            generate_manim(sample)

    def test_non_json_metadata_refuses(self):
        sample = example()
        sample["metrics"] = [{"label": "bad", "value": float("inf")}]
        with self.assertRaises(ValueError):
            generate_manim(sample)

    def test_mesh_face_budget_has_a_healthy_and_refused_twin(self):
        sample = example()
        mesh = sample["primitives"][-1]
        mesh["indices"] = [0, 1, 2, -1] * 1600
        generate_manim(sample)
        mesh["indices"].extend([0, 1, 2, -1])
        with self.assertRaisesRegex(ValueError, "MANIM_FACE_BUDGET"):
            generate_manim(sample)

    def test_limits_are_not_silent_geometry_decimation(self):
        sample = example()
        sample["primitives"][-1]["indices"] *= 23
        baked = json.loads(literal(generate_manim(sample), "SAMPLE_JSON"))
        self.assertEqual(baked["primitives"], sample["primitives"])

    def test_fixed_imports_and_no_latex_dependency(self):
        source = generate_manim(example())
        modules = [n.module for n in ast.parse(source).body if isinstance(n, ast.ImportFrom)]
        self.assertEqual(modules, ["manim"])
        self.assertNotIn("MathTex(", source)
        self.assertNotIn("Tex(", source)
        self.assertIn("--renderer=cairo", source)

    def test_default_kernel_samples_compile_if_present(self):
        try:
            from mathlab.kernel import evaluate
            from mathlab.catalog import catalog
        except ImportError:
            self.skipTest("Kernel is not yet available in this independent source-generation control")
        for lesson in catalog():
            with self.subTest(lesson=lesson["id"]):
                sample = evaluate(lesson["id"])
                source = generate_manim(sample)
                compile(source, lesson["id"] + ".py", "exec")
                self.assertEqual(json.loads(literal(source, "SAMPLE_JSON")), sample)


if __name__ == "__main__":
    unittest.main()
