import importlib.util
import unittest
from mathlab.catalog import catalog
from mathlab.kernel import evaluate
from mathlab.schema import lesson_card_schema


@unittest.skipUnless(importlib.util.find_spec('jsonschema'), 'Optional JSON Schema instrument not installed.')
class CardSchemaControls(unittest.TestCase):
    def setUp(self):
        from jsonschema import Draft202012Validator
        self.validator = Draft202012Validator(lesson_card_schema())

    def test_all_six_normalized_and_partial_cards_match_shared_domains(self):
        for lesson in catalog():
            for params in ({}, evaluate(lesson['id'])['params']):
                self.assertEqual(list(self.validator.iter_errors({'schema': 'x3d.mathlab.lesson-card/1', 'lesson': lesson['id'], 'params': params})), [])

    def test_domain_errors_and_unknown_fields_are_rejected(self):
        for lesson, params in [('linear', {'a': True}), ('derivative', {'h': 0}),
                               ('integral', {'n': 2.5}), ('fourier', {'terms': 13}),
                               ('lorenz', {'not_sigma': 10}), ('gradient', {'condition': 0})]:
            self.assertTrue(list(self.validator.iter_errors({'schema': 'x3d.mathlab.lesson-card/1', 'lesson': lesson, 'params': params})))
        self.assertTrue(list(self.validator.iter_errors({'schema': 'x3d.mathlab.lesson-card/1', 'lesson': 'linear', 'params': {}, 'code': 'not accepted'})))


if __name__ == '__main__':
    unittest.main()
