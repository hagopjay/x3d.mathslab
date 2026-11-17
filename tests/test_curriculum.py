"""Check authored discovery paths remain executable, exportable experiments."""
import json
import unittest
from urllib.parse import urlparse

from mathlab.catalog import catalog
from mathlab.cards import card_from_x3d
from mathlab.kernel import evaluate, normalize_params
from mathlab.manim_bridge import generate_manim
from mathlab.x3d import to_x3d


class CurriculumTests(unittest.TestCase):
    def test_every_authored_preset_is_a_valid_recoverable_world(self):
        count = 0
        for lesson in catalog():
            self.assertTrue(lesson.get('level'), lesson['id'])
            self.assertTrue(lesson.get('prerequisites'), lesson['id'])
            self.assertGreaterEqual(len(lesson.get('presets', [])), 2, lesson['id'])
            for preset in lesson['presets']:
                with self.subTest(lesson=lesson['id'], preset=preset['title']):
                    count += 1
                    self.assertTrue(preset['why'])
                    params = normalize_params(lesson['id'], preset['params'])
                    sample = evaluate(lesson['id'], params)
                    json.dumps(sample, allow_nan=False)
                    recovered = card_from_x3d(to_x3d(sample))
                    self.assertEqual(recovered['params'], params)
                    self.assertEqual(recovered['lesson'], lesson['id'])
        self.assertGreaterEqual(count, 50)

    def test_coordinate_captions_and_concept_bridges_are_complete(self):
        lessons = catalog()
        ids = {lesson['id'] for lesson in lessons}
        for lesson in lessons:
            self.assertIsInstance(lesson.get('axes'), str, lesson['id'])
            self.assertTrue(lesson['axes'].strip(), lesson['id'])
            self.assertGreaterEqual(len(lesson.get('connections', [])), 1, lesson['id'])
            for connection in lesson['connections']:
                self.assertIn(connection['lesson'], ids)
                self.assertNotEqual(connection['lesson'], lesson['id'])
                self.assertTrue(connection['why'])

    def test_resources_are_attributed_https_study_links(self):
        for lesson in catalog():
            self.assertTrue(lesson.get('resources'), lesson['id'])
            for resource in lesson['resources']:
                self.assertTrue(resource['title'])
                self.assertTrue(resource['note'])
                url = urlparse(resource['url'])
                self.assertEqual(url.scheme, 'https')
                self.assertTrue(url.netloc)

    def test_authored_view_policy_reaches_all_exporters(self):
        for lesson in catalog():
            with self.subTest(lesson=lesson['id']):
                sample = evaluate(lesson['id'])
                self.assertIn(sample['view'], ('planar', 'spatial'))
                self.assertEqual(sample['view'], lesson.get('view', 'planar'))
                source = generate_manim(sample)
                compile(source, '<baked ' + lesson['id'] + '>', 'exec')
                self.assertIn('SAMPLE.get("view") == "spatial"', source)


if __name__ == '__main__':
    unittest.main()
