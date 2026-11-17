"""Recover a lesson configuration from this adapter's X3D metadata.

Geometry is not imported: the declared parameters are normalized and the model
is regenerated. This distinguishes a parameter round trip from mesh editing.
"""
import hashlib
import json
import re
import xml.etree.ElementTree as ET

from .kernel import normalize_params

MAX_XML_BYTES = 2 * 1024 * 1024


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate metadata key: ' + key)
        result[key] = value
    return result


def card_from_x3d(text: str) -> dict:
    if not isinstance(text, str) or len(text.encode('utf-8')) > MAX_XML_BYTES:
        raise ValueError('X3D input exceeds its 2 MiB metadata-recovery budget.')
    if re.search(r'<!\s*(?:DOCTYPE|ENTITY)\b', text, re.I):
        raise ValueError('DTD and entity declarations are not part of this import policy.')
    try:
        root = ET.fromstring(text)
        if root.tag != 'X3D' or root.get('version') != '4.0':
            raise ValueError('Expected an exported X3D 4.0 document.')
        nodes = root.findall('./Scene/WorldInfo/MetadataString[@name="mathlab.sample"]')
        if len(nodes) != 1:
            raise ValueError('Expected one Math Lab model metadata record.')
        # The adapter emits one MFString item containing canonical JSON.
        encoded = json.loads(nodes[0].get('value', ''), object_pairs_hook=_unique)
        if not isinstance(encoded, str) or len(encoded.encode('utf-8')) > 65_536:
            raise ValueError('Invalid model metadata size or MFString encoding.')
        metadata = json.loads(encoded, object_pairs_hook=_unique)
        if not isinstance(metadata, dict) or metadata.get('adapter') != 'mathlab.x3d/1':
            raise ValueError('Unknown model metadata adapter.')
        lesson = metadata['lesson']
        if not isinstance(lesson, str):
            raise ValueError('Invalid lesson identifier.')
        params = normalize_params(lesson, metadata['parameters'])
        config = json.dumps({'lesson': lesson, 'params': params}, sort_keys=True,
                            separators=(',', ':'), ensure_ascii=False, allow_nan=False)
        if hashlib.sha256(config.encode('utf-8')).hexdigest() != metadata.get('configuration_sha256'):
            raise ValueError('Declared parameter identity does not match the metadata.')
    except (ET.ParseError, json.JSONDecodeError, KeyError, TypeError, RecursionError, OverflowError) as error:
        raise ValueError('Invalid Math Lab model metadata.') from error
    return {'schema': 'x3d.mathlab.lesson-card/1', 'lesson': lesson, 'params': params}
