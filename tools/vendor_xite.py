#!/usr/bin/env python3
"""Retain the pinned published X_ITE dist tree, assets and licenses unchanged."""
from pathlib import Path
import base64
import hashlib
import io
import json
import tarfile
from urllib.request import urlopen

VERSION = '16.8.0'
URL = 'https://registry.npmjs.org/x_ite/-/x_ite-16.8.0.tgz'
INTEGRITY = '1UzBekEiS+KliulxGxmKAV8RUGvvcuKGaGuGzjoUd73vJ5WG0VdGOP+gHomAawvgMpXQ4Z8WW1XHfTIn7Wc0ew=='
ROOT = Path(__file__).resolve().parents[1]


def install(data: bytes):
    if base64.b64encode(hashlib.sha512(data).digest()).decode() != INTEGRITY:
        raise ValueError('Published archive integrity mismatch.')
    target = ROOT / 'web' / 'vendor' / 'x_ite'
    inventory = {}
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
        size = 0
        for member in archive.getmembers():
            path = Path(member.name)
            if not member.isfile() or path.is_absolute() or '..' in path.parts or path.parts[0] != 'package':
                continue
            relative = Path(*path.parts[1:])
            name = relative.as_posix()
            if not (name.startswith(('dist/', 'LICENSES/')) or name in ('LICENSE.md', 'package.json')):
                continue
            size += member.size
            if size > 40 * 1024 * 1024:
                raise ValueError('Published runtime exceeds declared 40 MiB expansion budget.')
            content = archive.extractfile(member).read()
            destination = target / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(content)
            inventory[name] = {'bytes': len(content), 'sha256': hashlib.sha256(content).hexdigest()}
    origin = {'schema': 'mathlab.vendor/1', 'name': 'x_ite', 'version': VERSION,
              'source': URL, 'archive_sha512_base64': INTEGRITY,
              'scope': 'Entire published dist tree plus package metadata, primary and bundled licenses; unmodified bytes.',
              'files': inventory}
    (target / 'ORIGIN.json').write_text(json.dumps(origin, indent=2) + '\n')
    return origin


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path)
    args = parser.parse_args()
    raw = args.archive.read_bytes() if args.archive else urlopen(URL, timeout=60).read(20 * 1024 * 1024)
    manifest = install(raw)
    print(json.dumps({'version': VERSION, 'files': len(manifest['files']),
                      'bytes': sum(v['bytes'] for v in manifest['files'].values())}))
