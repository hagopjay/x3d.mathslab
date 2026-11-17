# Shared Math Lab sample → Manim film

`mathlab.manim_bridge.generate_manim(sample)` produces a complete Python file
containing `MathlabScene(ThreeDScene)`. Generation does not import Manim, create
a subprocess, execute input code or call an external service. The interactive
lab can export the source without installing Manim or obtaining an API key.

The adapter validates the same sample boundary as native X3D export, then embeds
the complete canonical sample JSON and its SHA-256. Its source checks that digest
before loading the retained data. Titles and parameters are JSON data inside a
Python string literal; they are not interpolated into Python statements.
The digest identifies the retained sample bytes. It is not publisher
authentication, a complete render-environment identity or an acceptance receipt.

## What is preserved

The line vertices, mesh vertices and face indices, sphere positions/radii, box
positions/dimensions, declared colors, transparency, lesson parameters, metrics
and explanatory text remain in `SAMPLE_JSON`. The generated scene draws those
primitives. It does not solve Lorenz again, estimate another derivative, integrate
another function or reconstruct a visually similar surface from a second formula.

Manim applies one common translation and positive uniform scale to frame the
geometry. The view transform therefore changes display coordinates; it does not
change the retained mathematical sample. Two-dimensional lessons use a front
camera. Lorenz and gradient lessons use an angled three-dimensional view.
Colors become 8-bit display colors; viewport, lighting, line thickness, fonts and
polygon shading differ from X_ITE. Pixel parity is not claimed.

The film is an editorial reveal of one sample: title, two bounded headline
readouts, surfaces, line traces, markers and a final comparison pause. Caption
length and visible parameter count are bounded; full values remain in the
embedded JSON. Its nominal timeline is 9.2 seconds.
Drawing a curve progressively is not a claim that each film frame is an ODE time,
that a sampled trajectory is an analytic solution, or that this video retains
interactive continuation state. An interactive parameter sweep would require
several explicitly evaluated sample frames and a separate timeline contract.

## Work limits

Native X3D sample validation runs first. The bridge additionally refuses baked
JSON larger than 2 MiB and meshes exceeding 1,600 total faces. It does not silently
drop triangles or decimate a curve to pass the cap. These are source-generation
budgets, not render-time or memory guarantees. Cairo still has to rasterize the
result, and an optional low-quality render is the appropriate first smoke test.

The scene uses `Text` rather than `Tex`/`MathTex`, avoiding a LaTeX requirement.
It uses Cairo-compatible `ThreeDScene`, `VMobject`, `Polygon`, `Cube` and `Sphere`
objects; it does not require OpenGL merely because the lesson has 3D coordinates.

## Running the optional film

After reviewing the generated file in an environment with Manim Community and
its system dependencies installed:

```sh
manim -ql --renderer=cairo lesson.py MathlabScene
```

This is trusted local Python execution. Neither a valid scene name, JSON
validation, AST syntax checking nor the attachment's Manim diagnostics sandbox
arbitrary Python. The browser API only returns generated source; it does not
offer arbitrary-code rendering. The optional Manim MCP CLI has its own separate
execution and artifact contract.

## Evidence

`tests/test_bridge.py` checks complete-source syntax, literal data/digest
retention, determinism, non-mutation, malicious-text containment, nonfinite input
refusal, face-budget twins, fixed imports and the six available default kernels.
These are source-generation/data controls. They do not establish successful
Manim execution, visible output, GPU behavior, typography quality or educational
effectiveness. Any actual rendered sample must be recorded separately in the
release evidence, including Manim version, renderer, quality and source identity.

Primary API references used for the scene design:

- https://docs.manim.community/en/stable/reference/manim.scene.three_d_scene.ThreeDScene.html
- https://docs.manim.community/en/stable/reference/manim.mobject.types.vectorized_mobject.VMobject.html
