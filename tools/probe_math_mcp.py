"""Probe the optional Math Lab MCP server through the official stdio client.

Records transport checks and identities, never full geometry or generated source.
This probe performs no Manim execution and needs only the optional MCP SDK.
"""
from __future__ import annotations
import argparse
import asyncio
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import re
import sys
from datetime import datetime, timezone

def ga(obj, camel):
    """Read an MCP model attribute under mcp 1.x camelCase or 2.x snake_case."""
    if hasattr(obj, camel):
        return getattr(obj, camel)
    return getattr(obj, re.sub(r'([A-Z])', lambda m: '_' + m.group(1).lower(), camel))


ROOT = Path(__file__).resolve().parents[1]


def sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode('utf-8')


def data(result):
    if ga(result, "isError"):
        raise ValueError('MCP tool reported an error: ' + str(result.content)[:400])
    if ga(result, "structuredContent") is not None:
        return ga(result, "structuredContent")
    for block in result.content:
        if block.type == 'text':
            value = json.loads(block.text)
            if isinstance(value, dict):
                return value
    raise ValueError('No structured object returned by tool.')


async def probe() -> dict:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    checks = []
    started = datetime.now(timezone.utc).isoformat()
    parameters = StdioServerParameters(command=sys.executable,
                                       args=['-m', 'mathlab.mcp_server'], cwd=str(ROOT))
    async with stdio_client(parameters) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            initialized = await session.initialize()
            checks.append({'id': 'stdio_initialize', 'pass': bool(ga(initialized, "protocolVersion")),
                           'protocol': ga(initialized, "protocolVersion"),
                           'server': ga(initialized, "serverInfo").model_dump(mode='json')})
            inventory = await session.list_tools()
            names = {tool.name for tool in inventory.tools}
            expected = {'mathlab_list_lessons', 'mathlab_scene', 'mathlab_manim_source'}
            checks.append({'id': 'three_read_only_tools', 'pass': names == expected and
                           all(tool.annotations and ga(tool.annotations, "readOnlyHint")
                               for tool in inventory.tools), 'names': sorted(names)})
            lessons = data(await session.call_tool('mathlab_list_lessons'))
            expected_lessons = {'linear', 'derivative', 'integral', 'fourier', 'lorenz', 'gradient',
                                'complex', 'taylor', 'waves', 'probability', 'least_squares', 'vector_field',
                                'svd', 'bayes', 'lagrange', 'aliasing', 'heat', 'refraction'}
            checks.append({'id': 'catalog_call', 'pass': {row['id'] for row in lessons.get('lessons', [])} == expected_lessons,
                           'lessons': [row['id'] for row in lessons['lessons']]})
            scene = data(await session.call_tool('mathlab_scene',
                        {'lesson': 'derivative', 'params': {'x': 1, 'h': .1}}))
            identity = scene['identity']
            valid = (scene['sample']['lesson'] == 'derivative' and '<X3D' in scene['x3d'] and
                     identity['x3d_sha256'] == sha(scene['x3d'].encode()) and
                     identity['sample_sha256'] == sha(canonical(scene['sample'])))
            checks.append({'id': 'derivative_scene_call', 'pass': valid,
                           'x3d_bytes': len(scene['x3d'].encode()),
                           'sample_sha256': identity['sample_sha256'],
                           'x3d_sha256': identity['x3d_sha256'],
                           'source_sha256': identity['source_sha256']})
            source = data(await session.call_tool('mathlab_manim_source',
                         {'lesson': 'derivative', 'params': {'x': 1, 'h': .1}}))
            checks.append({'id': 'baked_source_same_sample',
                           'pass': source['identity']['sample_sha256'] == identity['sample_sha256'] and
                           source['identity']['manim_source_sha256'] == sha(source['source'].encode()),
                           'source_bytes': len(source['source'].encode()),
                           'source_sha256': source['identity']['manim_source_sha256']})
            for key in sorted(expected_lessons - {'derivative'}):
                result = data(await session.call_tool('mathlab_scene', {'lesson': key}))
                checks.append({'id': key + '_scene_call',
                               'pass': result['sample']['lesson'] == key and
                               result['identity']['x3d_sha256'] == sha(result['x3d'].encode()),
                               'x3d_bytes': len(result['x3d'].encode())})
            refused = await session.call_tool('mathlab_scene',
                        {'lesson': 'derivative', 'params': {'x': True}})
            checks.append({'id': 'boolean_parameter_refused', 'pass': bool(ga(refused, "isError"))})
    report = {'schema': 'mathlab.mcp-stdio-probe/1', 'started_utc': started,
              'finished_utc': datetime.now(timezone.utc).isoformat(),
              'status': 'pass' if all(row['pass'] for row in checks) else 'fail',
              'python': platform.python_version(), 'mcp_sdk': importlib.metadata.version('mcp'),
              'instrument_sha256': sha(Path(__file__).read_bytes()),
              'adapter_sha256': sha((ROOT / 'mathlab/mcp_server.py').read_bytes()),
              'checks': checks,
              'limitations': ['One local Python/SDK executor using the actual stdio transport.',
                              'No Manim rendering or generated/user-supplied code execution, network transport, browser or formal acceptance ran.']}
    report['report_sha256'] = sha(canonical(report))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'receipts/math-mcp.json')
    args = parser.parse_args()
    report = asyncio.run(probe())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'checks': len(report['checks']),
                      'mcp_sdk': report['mcp_sdk'], 'output': str(args.output)}))
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
