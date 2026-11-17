import json
import unittest
import xml.etree.ElementTree as ET
from mathlab.catalog import catalog
from mathlab.kernel import evaluate
from mathlab.x3d import to_x3d
from mathlab.cards import card_from_x3d


class CardControls(unittest.TestCase):
    def test_six_exported_worlds_recover_the_same_normalized_parameters(self):
        for lesson in catalog():
            sample = evaluate(lesson['id'])
            card = card_from_x3d(to_x3d(sample))
            self.assertEqual(card['params'], sample['params'])
            self.assertEqual(to_x3d(evaluate(card['lesson'], card['params'])), to_x3d(sample))

    def test_geometry_edits_do_not_silently_become_model_parameter_edits(self):
        xml = to_x3d(evaluate('linear'))
        root = ET.fromstring(xml)
        root.find('.//Coordinate').set('point', '0 0 0 1 1 1')
        self.assertEqual(card_from_x3d(ET.tostring(root, encoding='unicode')), card_from_x3d(xml))

    def test_unsupported_and_ambiguous_metadata_refuses(self):
        original = to_x3d(evaluate('fourier'))
        for bad in ('<X3D/>', '<!DOCTYPE X3D><X3D/>', original.replace('mathlab.sample', 'other.sample'),
                    original.replace('mathlab.x3d/1', 'mathlab.x3d/999')):
            with self.subTest(bad=bad[:50]), self.assertRaises(ValueError):
                card_from_x3d(bad)
        root = ET.fromstring(original)
        info = root.find('./Scene/WorldInfo')
        info.append(ET.fromstring(ET.tostring(info[0])))
        with self.assertRaises(ValueError):
            card_from_x3d(ET.tostring(root, encoding='unicode'))

    def test_changed_parameter_with_stale_identity_refuses(self):
        root = ET.fromstring(to_x3d(evaluate('derivative')))
        node = root.find('./Scene/WorldInfo/MetadataString')
        metadata = json.loads(json.loads(node.get('value')))
        metadata['parameters']['x'] = 1.2
        node.set('value', json.dumps(json.dumps(metadata)))
        with self.assertRaisesRegex(ValueError, 'identity'):
            card_from_x3d(ET.tostring(root, encoding='unicode'))


if __name__ == '__main__':
    unittest.main()
