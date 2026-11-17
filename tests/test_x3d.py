"""Standard-library adapter controls; external schema/render checks are separate."""

from copy import deepcopy
import json
import math
import re
import unittest
import xml.etree.ElementTree as ET

from mathlab.x3d import MAX_INDICES, MAX_POINTS, MAX_PRIMITIVES, to_x3d


def specimen():
    return {
        "schema": "mathlab.sample/1", "lesson": "fixture", "title": "Geometry & parameters",
        "params": {"phase": 0.25}, "metrics": [{"id": "m", "label": "reference", "value": 1.25}],
        "insights": ["The input is a sampled picture."],
        "bounds": {"center": [0, 0, 0], "size": [6, 5, 4]},
        "primitives": [
            {"kind": "line", "id": "line-a", "points": [[-1, 0, 0], [1, 1, 0]], "color": [0.2, 0.8, 1]},
            {"kind": "sphere", "id": "point-a", "position": [0, 0, 1], "radius": 0.15, "color": [1, 0.6, 0.1]},
            {"kind": "mesh", "id": "surface-a", "points": [[0, 0, 0], [1, 0, 0], [0, 1, 0]],
             "indices": [0, 1, 2, -1], "color": [0.5, 0.7, 1], "transparency": 0.2},
            {"kind": "box", "id": "area-a", "position": [0, -0.5, 0], "size": [0.5, 1, 0.1], "color": [0.5, 1, 0.7]},
        ],
    }


def metadata(root):
    value = root.find(".//WorldInfo/MetadataString").attrib["value"]
    # Decode one MFString item (backslash/quote escaping), then its JSON document.
    text = re.sub(r"\\([\\\"])", r"\1", value[1:-1])
    return json.loads(text)


class X3DAdapterTests(unittest.TestCase):
    def test_four_kinds_generate_native_nodes_and_deterministic_bytes(self):
        sample = specimen(); before = deepcopy(sample)
        document = to_x3d(sample)
        self.assertEqual(document, to_x3d(sample))
        self.assertEqual(sample, before)
        root = ET.fromstring(document)
        self.assertEqual(root.attrib, {"profile": "Immersive", "version": "4.0"})
        for tag in ("IndexedLineSet", "Sphere", "IndexedFaceSet", "Box", "Viewpoint"):
            self.assertIsNotNone(root.find(".//" + tag))
        self.assertEqual(root.find(".//Viewpoint").attrib["DEF"], "MathLabView")

    def test_metadata_precedes_shape_appearance_and_geometry(self):
        root = ET.fromstring(to_x3d(specimen()))
        shapes = root.findall(".//Group[@DEF='MathLabModel']//Shape")
        self.assertEqual(len(shapes), 4)
        for shape in shapes:
            self.assertEqual(shape[0].tag, "MetadataString")
            self.assertEqual(shape[1].tag, "Appearance")
            self.assertEqual(len(shape), 3)

    def test_parameter_metadata_round_trip_and_content_identity(self):
        first = metadata(ET.fromstring(to_x3d(specimen())))
        self.assertEqual(first["parameters"], {"phase": 0.25})
        self.assertEqual(first["lesson"], "fixture")
        self.assertEqual(len(first["configuration_sha256"]), 64)
        changed = specimen(); changed["primitives"][0]["points"][0][0] = -2
        second = metadata(ET.fromstring(to_x3d(changed)))
        self.assertEqual(first["configuration_sha256"], second["configuration_sha256"])
        self.assertNotEqual(first["sample_sha256"], second["sample_sha256"])

    def test_xml_and_mfstring_escaping_cannot_insert_nodes(self):
        sample = specimen()
        sample["title"] = 'Quoted "curve" & <Script> Ω'
        sample["params"] = {"note": 'a \\ b "quoted" <Script url="remote"/>'}
        sample["primitives"][0]["id"] = 'odd id " & <script>'
        document = to_x3d(sample); root = ET.fromstring(document)
        self.assertEqual(root.find(".//WorldInfo").attrib["title"], sample["title"])
        self.assertEqual(metadata(root)["parameters"], sample["params"])
        self.assertEqual(root.findall(".//Script"), [])
        for node in root.iter():
            self.assertNotIn("url", node.attrib)
        self.assertNotIn("<!DOCTYPE", document)
        self.assertNotIn("<!ENTITY", document)

    def test_generated_defs_are_valid_unique_and_independent_of_source_id_syntax(self):
        sample = specimen(); sample["primitives"][0]["id"] = "99 unsafe id"
        root = ET.fromstring(to_x3d(sample)); defs = [n.attrib["DEF"] for n in root.iter() if "DEF" in n.attrib]
        self.assertEqual(len(defs), len(set(defs)))
        self.assertTrue(all(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value) for value in defs))
        self.assertFalse(any("USE" in n.attrib for n in root.iter()))

    def test_invalid_coordinate_and_healthy_twin(self):
        for value in (math.nan, math.inf, -math.inf, True, "1", 10**400):
            with self.subTest(value=type(value).__name__):
                sample = specimen(); sample["primitives"][0]["points"][0][0] = value
                with self.assertRaisesRegex(ValueError, "X3D_NUMBER"):
                    to_x3d(sample)
        self.assertIn("IndexedLineSet", to_x3d(specimen()))

    def test_nonfinite_metadata_is_refused(self):
        sample = specimen(); sample["params"]["phase"] = math.nan
        with self.assertRaisesRegex(ValueError, "X3D_METADATA"):
            to_x3d(sample)
        sample = specimen(); sample["metrics"][0]["value"] = math.inf
        with self.assertRaisesRegex(ValueError, "X3D_METADATA"):
            to_x3d(sample)

    def test_invalid_color_and_transparency_are_refused(self):
        for field, value in (("color", [1.1, 0, 0]), ("color", [-0.1, 0, 0]), ("transparency", 2), ("transparency", -1)):
            sample = specimen(); sample["primitives"][0][field] = value
            with self.assertRaises(ValueError):
                to_x3d(sample)

    def test_duplicate_source_id_is_refused_without_mutation(self):
        sample = specimen(); sample["primitives"][1]["id"] = sample["primitives"][0]["id"]
        before = deepcopy(sample)
        with self.assertRaisesRegex(ValueError, "X3D_ID"):
            to_x3d(sample)
        self.assertEqual(sample, before)

    def test_mesh_reference_and_face_controls(self):
        for indices in ([0, 1, 8, -1], [0, 1, -1], [0, 1, 1, -1], [-1], [0, 1, True, -1], [0, 1, -2, -1]):
            sample = specimen(); sample["primitives"][2]["indices"] = indices
            with self.assertRaisesRegex(ValueError, "X3D_INDICES"):
                to_x3d(sample)
        sample = specimen(); sample["primitives"][2]["indices"] = [0, 1, 2]
        root = ET.fromstring(to_x3d(sample))
        self.assertEqual(root.find(".//IndexedFaceSet").attrib["coordIndex"], "0 1 2 -1")

    def test_collapsed_matrix_geometry_can_remain_a_valid_sample(self):
        sample = specimen(); sample["primitives"][2]["points"] = [[0, 0, 0], [1, 0, 0], [2, 0, 0]]
        self.assertIsNotNone(ET.fromstring(to_x3d(sample)).find(".//IndexedFaceSet"))

    def test_positive_physical_primitive_dimensions_are_required(self):
        for index, field, value in ((1, "radius", 0), (1, "radius", -0.1), (3, "size", [1, 0, 1]), (3, "size", [1, -1, 1])):
            sample = specimen(); sample["primitives"][index][field] = value
            with self.assertRaisesRegex(ValueError, "X3D_GEOMETRY|X3D_NUMBER"):
                to_x3d(sample)

    def test_planar_camera_and_deep_camera_remain_finite(self):
        sample = specimen(); sample["bounds"]["size"] = [6, 5, 0]
        view = ET.fromstring(to_x3d(sample)).find(".//Viewpoint")
        self.assertEqual(view.attrib["orientation"], "0 0 1 0")
        deep = ET.fromstring(to_x3d(specimen())).find(".//Viewpoint")
        self.assertNotEqual(deep.attrib["orientation"], "0 0 1 0")
        for node in (view, deep):
            self.assertTrue(all(math.isfinite(float(x)) for key in ("position", "orientation", "centerOfRotation") for x in node.attrib[key].split()))

    def test_area_box_thickness_does_not_tilt_the_authored_plane_lesson(self):
        sample = specimen(); sample["lesson"] = "integral"; sample["bounds"]["size"] = [7, 4.4, .6]
        view = ET.fromstring(to_x3d(sample)).find(".//Viewpoint")
        self.assertEqual(view.attrib["orientation"], "0 0 1 0")

    def test_bad_bounds_and_schema_are_refused(self):
        for bounds in ({"center": [0, 0], "size": [1, 1, 1]}, {"center": [0, 0, 0], "size": [0, 0, 0]}, {"center": [0, 0, 0], "size": [1, -1, 0]}):
            sample = specimen(); sample["bounds"] = bounds
            with self.assertRaises(ValueError):
                to_x3d(sample)
        sample = specimen(); sample["schema"] = "other/1"
        with self.assertRaisesRegex(ValueError, "X3D_SAMPLE"):
            to_x3d(sample)

    def test_aggregate_point_and_primitive_budgets(self):
        sample = specimen(); sample["primitives"] = [{"kind": "line", "id": "too-large", "points": [[0, 0, 0]] * (MAX_POINTS + 1)}]
        with self.assertRaisesRegex(ValueError, "X3D_BUDGET"):
            to_x3d(sample)
        sample = specimen(); sample["primitives"] = [{"kind": "sphere", "id": str(i), "position": [0, 0, 0], "radius": 1} for i in range(MAX_PRIMITIVES + 1)]
        with self.assertRaisesRegex(ValueError, "X3D_BUDGET"):
            to_x3d(sample)

    def test_index_metadata_and_text_budgets(self):
        sample = specimen(); sample["primitives"][2]["indices"] = [0, 1, 2, -1] * (MAX_INDICES // 4 + 1)
        with self.assertRaisesRegex(ValueError, "X3D_BUDGET"):
            to_x3d(sample)
        sample = specimen(); sample["params"] = {"text": "a" * 65_536}
        with self.assertRaisesRegex(ValueError, "X3D_BUDGET"):
            to_x3d(sample)
        sample = specimen(); sample["title"] = "bad\x00title"
        with self.assertRaisesRegex(ValueError, "X3D_TEXT"):
            to_x3d(sample)

    def test_unknown_geometry_is_refused_not_silently_dropped(self):
        sample = specimen(); sample["primitives"][0]["kind"] = "Script"
        with self.assertRaisesRegex(ValueError, "X3D_PRIMITIVE"):
            to_x3d(sample)


if __name__ == "__main__":
    unittest.main()
