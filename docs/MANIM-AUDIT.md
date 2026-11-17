# Manim v2 audit and bounded v2.1 repairs

The supplied archive contains the active v2 server and older v0.2 tests. Its
handoff reports earlier renders on another machine, but the archive does not
contain those videos, that virtual environment or a verified current connection.
Those historical statements are not fresh evidence for this delivery. The
`manim_src/` reference and original handoff documents remain unchanged.

The Math Lab's interactive HTTP application does not execute supplied Python.
The separate, optional Manim MCP command does: a render script runs with the
server account's permissions and inherited environment. Identifier checks,
AST inspection and subprocess argument lists do not make that execution a
sandbox. Use the MCP renderer for trusted local scripts; a multi-user service
would require a separately designed isolation and authorization boundary.

## Source findings and repairs

| Supplied behavior | Consequence | v2.1 repair and control |
|---|---|---|
| Scene discovery used a regular expression | Comments and strings can resemble classes; aliases/local inheritance are missed | AST discovery supports imported aliases and local Scene inheritance without executing imports; decoy and healthy-class controls |
| Cache IDs included only code, scene and quality | A changed engine could reuse an earlier result | Cache context includes declared engine/executable identity; engine-twin identity control |
| Any existing MP4 counted as a cache hit | Missing metadata or altered video bytes can look complete | Metadata is the final commit marker; cache schema/context and video SHA-256 must match; corrupted-video and missing-sidecar controls |
| Video/preview publication used final paths directly | Concurrent readers could observe partial artifacts | Unique temporary files and atomic replacements; metadata commits last; duplicate same-ID requests serialize |
| A semaphore existed only inside each batch call | Separate batches and single requests could exceed the intended global budget | All render jobs share one process-wide 1–4 cap; a mixed single/batch control measures peak instrumented concurrency |
| A timeout killed the immediate process without awaiting it | Child lifecycle and output cleanup were incomplete | Timeout and cancellation kill and await the child; POSIX jobs start a session and cleanup targets that process group |
| Render output was collected without a size bound | Long diagnostic streams could grow response memory | Drain both streams while retaining only a 128 KiB tail per stream; large/small stream controls |
| FFmpeg preview extraction blocked the async function | A preview could stall unrelated MCP work | Preview extraction runs through `asyncio.to_thread`; an instrumented heartbeat advances while a slow preview runs |
| Video discovery took the first MP4 recursively | A partial clip or another scene could be copied as the final result | Require a nonempty final MP4 matching the requested scene; exclude `partial_movie_files` |
| `get_render_info` joined a caller ID into a path | A path-like ID could address files outside the render namespace | Strict render-ID grammar, resolved-parent containment and symlink refusal; traversal and symlink controls |
| Sidecar fields were flattened over response fields | Metadata could replace the reported path or status | Return sidecars under `metadata`; reserved-field override control |
| Negative cleanup counts used Python slicing semantics | An invalid count could delete a surprising set | Integer range checks, active-render preservation and symlink-safe cleanup controls |
| Unbounded/invalid configuration, code and batch values | Resource or CLI behavior depended on accidental coercion | Explicit configuration ranges, a 256 KiB code budget, known quality names and at most sixteen batch targets |

These are scoped repairs to a trusted-local adapter. The server is not a
multi-tenant process manager. On non-POSIX systems cleanup kills and awaits the
immediate child; this delivery does not claim complete descendant termination
on Windows. Access by another process that can freely rewrite the output
directory is also outside the containment model.

## Cache and artifact identity

Render IDs now use a 24-hex-character SHA-256 prefix over canonical code digest,
scene, quality and engine context. That context records the resolved executable,
its bytes when at most 64 MiB, the Manim distribution visible to the server's
Python interpreter, Python version and `MANIM_CACHE_EPOCH`. Larger executables
use size/mtime and record that weaker scope. An external executable can use a
different interpreter from the server. Plugins, fonts, assets, environment and
hardware are not comprehensively fingerprinted.

Therefore the context prevents several accidental stale-cache cases but does
not establish whole-environment reproducibility. Increment `MANIM_CACHE_EPOCH`
or clear the relevant cache when external inputs change. Existing legacy files
remain listable under the bounded ID grammar; they are not accepted as fresh
schema-2 cache entries without matching metadata and a verified video digest.

The optional preview is a final-frame extraction, not proof that an entire
animation remained visible or mathematically correct. Base64 has a separate
size budget. Quality time estimates remain explicitly uncalibrated source
heuristics, rather than measured render-time promises. Three-dimensional Manim
scenes do not inherently require OpenGL; backend choice needs actual testing.

## Executed controls

Run:

```sh
python3 -m unittest discover -s tests -p test_manim_v2.py -v
```

**Eighteen tests pass** against the actual v2.1 module. MCP registration uses an
explicit in-test adapter because a live MCP transport is a separate integration
boundary. Render-control tests use instrumented subprocess results and fake
payload bytes; those payloads are never presented as actual media.

The executed domains are: AST discovery; identifier/engine identity; environment
ranges; input refusal; duplicate jobs; shared concurrency; cache commit/digest;
final-video selection; nonblocking preview scheduling; timeout; cancellation;
bounded output; ID/symlink containment; cleanup; sidecar ownership; batch/time-
estimate scope; and static-validation diagnostics. One additional lifecycle
instrument inside this eighteen-test set starts an owned Python process and
actually kills/awaits it. That is a child-lifecycle observation, not a Manim
render or an operating-system isolation proof.

No fresh Manim video, actual FFmpeg preview, live SDK/MCP client exchange,
backend comparison, codec-quality measurement or Windows descendant-lifecycle
run is claimed by these tests. The accepted dependency ranges in `pyproject.toml`
are resolver constraints, not a tested cross-version compatibility matrix.

## Relationship to X3D Math Lab

Math Lab retains lesson parameters and mathematical model data independently
from the renderer. X3D exports and generated Manim scripts can explain the same
lesson while remaining different presentation artifacts. A schema-valid X3D
file, a syntax-valid Manim script and a completed MP4 are three different
checks. None establishes the others by implication.

A future render receipt should name lesson/model identity, normalized parameters,
generated source identity, actual renderer/dependencies, output identity,
mathematical diagnostics and observed visibility. That is a useful extension
path; this adapter's cache sidecar is not a complete educational proof receipt.
