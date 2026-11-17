"""Optional read-only Math Lab tools over the official MCP stdio transport.

This server evaluates enumerated mathematical models and generates source text.
It never imports Manim, renders supplied Python or accepts arbitrary expressions.
Run separately from the legacy trusted-local code renderer:
    python -m mathlab.mcp_server
"""
from __future__ import annotations

import asyncio
import hashlib
import math
from typing import Any

try:  # mcp 1.x
    from mcp.server.fastmcp import FastMCP
except ModuleNotFoundError:  # mcp 2.x renamed FastMCP to MCPServer
    from mcp.server.mcpserver import MCPServer as FastMCP
from mcp.types import ToolAnnotations

from .server import MAX_RESPONSE, canonical, decode_request, evaluate_request, verify_producers

mcp = FastMCP(
    'x3d-mathlab',
    instructions=(
        'Explore six enumerated mathematical lessons. List lessons, evaluate a '
        'bounded parameter card into sampled data and X3D, or generate an inspectable '
        'Manim source snapshot. These tools do not render or execute supplied code. '
        'A generated source file would require a separate trusted-local execution step.'
    ),
)
_READ_ONLY = ToolAnnotations(readOnlyHint=True, destructiveHint=False,
                             idempotentHint=True, openWorldHint=False)
_JOBS = asyncio.Semaphore(4)


def _request(lesson: str, params: dict[str, Any] | None) -> dict:
    """Apply the same request gate as HTTP, without Pydantic numeric coercion."""
    params = {} if params is None else params
    # Bound the shallow input before serialization. The shared decoder remains
    # authoritative for the complete byte/domain contract.
    if not isinstance(params, dict) or len(params) > 16:
        raise ValueError('params must be an object with at most sixteen numeric values.')
    for key, value in params.items():
        if (not isinstance(key, str) or len(key) > 32 or isinstance(value, bool)
                or not isinstance(value, (int, float))):
            raise ValueError('Parameters require short names and numeric values.')
        try:
            finite = math.isfinite(value)
        except OverflowError as error:
            raise ValueError('Parameter magnitude is too large.') from error
        if not finite:
            raise ValueError('Parameters must be finite.')
    try:
        return decode_request(canonical({'lesson': lesson, 'params': params}))
    except (TypeError, RecursionError) as error:
        raise ValueError('Expected a bounded lesson identifier and numeric parameter object.') from error


def _bounded(value: dict) -> dict:
    if len(canonical(value)) > MAX_RESPONSE:
        raise ValueError('Generated response exceeds the declared 4 MiB budget.')
    return value


@mcp.tool(annotations=_READ_ONLY)
async def mathlab_list_lessons() -> dict:
    """List the available lessons, parameter domains, explanations and challenges."""
    def read():
        from .catalog import catalog
        verify_producers()
        result = {'lessons': catalog()}
        verify_producers()
        return _bounded(result)
    async with _JOBS:
        return await asyncio.to_thread(read)


@mcp.tool(annotations=_READ_ONLY)
async def mathlab_scene(lesson: str, params: dict[str, Any] | None = None) -> dict:
    """Evaluate one known lesson card and return its actual sample, X3D and identities."""
    request = _request(lesson, params)
    async with _JOBS:
        return await asyncio.to_thread(lambda: _bounded(evaluate_request(request)))


@mcp.tool(annotations=_READ_ONLY)
async def mathlab_manim_source(lesson: str, params: dict[str, Any] | None = None) -> dict:
    """Generate a baked Manim source snapshot from the same model, without running it."""
    request = _request(lesson, params)
    def generate():
        from .manim_bridge import BRIDGE_VERSION, generate_manim
        result = evaluate_request(request)
        source = generate_manim(result['sample'])
        verify_producers()
        return _bounded({
            'schema': 'mathlab.manim-source/1', 'lesson': result['sample']['lesson'],
            'params': result['sample']['params'], 'source': source,
            'identity': {**result['identity'], 'bridge': BRIDGE_VERSION,
                         'manim_source_sha256': hashlib.sha256(source.encode('utf-8')).hexdigest(),
                         'execution': 'Source text generated only; Manim was not imported or run.'},
        })
    async with _JOBS:
        return await asyncio.to_thread(generate)


def main():
    mcp.run(transport='stdio')


if __name__ == '__main__':
    main()
