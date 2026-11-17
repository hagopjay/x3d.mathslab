#!/usr/bin/env python3
"""Recover an exported X3D's parameters as a lesson card; never load its geometry."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mathlab.cards import card_from_x3d, MAX_XML_BYTES

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('x3d', type=Path)
parser.add_argument('output', type=Path)
args = parser.parse_args()
if args.x3d.stat().st_size > MAX_XML_BYTES:
    parser.error('Input exceeds the 2 MiB recovery budget.')
card = card_from_x3d(args.x3d.read_text(encoding='utf-8'))
args.output.write_text(json.dumps(card, indent=2, ensure_ascii=False) + '\n')
print('Recovered', card['lesson'], 'parameters. Open the JSON card in Math Lab to regenerate the model.')
