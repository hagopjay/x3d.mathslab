#!/usr/bin/env python3
"""Bake reproducible lesson cards, native X3D and corresponding Manim sources."""
import hashlib
import json
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from mathlab.catalog import catalog
from mathlab.kernel import evaluate
from mathlab.x3d import to_x3d
from mathlab.manim_bridge import generate_manim
from mathlab.schema import lesson_card_schema


def main():
    report = {'schema': 'mathlab.example-build/1', 'python': platform.python_version(),
              'source_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in sorted((ROOT / 'mathlab').glob('*.py'))}, 'examples': []}
    for directory in ('cards', 'x3d', 'manim'):
        (ROOT / 'examples' / directory).mkdir(parents=True, exist_ok=True)
    (ROOT / 'schemas').mkdir(exist_ok=True)
    schema_bytes = (json.dumps(lesson_card_schema(), indent=2, ensure_ascii=False) + '\n').encode('utf-8')
    (ROOT / 'schemas' / 'lesson-card.schema.json').write_bytes(schema_bytes)
    report['card_schema_sha256'] = hashlib.sha256(schema_bytes).hexdigest()
    for lesson in catalog():
        key = lesson['id']
        sample = evaluate(key)
        card = {'schema': 'x3d.mathlab.lesson-card/1', 'lesson': key, 'params': sample['params']}
        outputs = {'cards/' + key + '.json': json.dumps(card, indent=2, ensure_ascii=False) + '\n',
                   'x3d/' + key + '.x3d': to_x3d(sample),
                   'manim/' + key + '.py': generate_manim(sample)}
        row = {'lesson': key, 'metrics': sample['metrics'], 'files': {}}
        for name, text in outputs.items():
            content = text.encode('utf-8')
            (ROOT / 'examples' / name).write_bytes(content)
            row['files']['examples/' + name] = {'bytes': len(content), 'sha256': hashlib.sha256(content).hexdigest()}
        report['examples'].append(row)
        print(key, len(sample['primitives']), 'primitives,', len(outputs['x3d/' + key + '.x3d'].encode()), 'X3D bytes')
    (ROOT / 'receipts' / 'example-build.json').write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + '\n')


if __name__ == '__main__':
    main()
