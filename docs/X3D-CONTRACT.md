# Native X3D contract

`mathlab.x3d.to_x3d(sample)` turns one finite Math Lab sample into a deterministic,
self-contained X3D 4.0 XML document. The exported picture uses native standard
nodes. It is not a screen capture and does not depend on Three.js.

The Python mathematical kernel owns numerical values. This adapter owns their
scene representation. The HTML lesson controller owns questions, parameter
widgets, story progression, animation policy and accessible explanations.
Those are related artifacts with different responsibilities.

## Input and mapping

The required envelope is `schema: "mathlab.sample/1"`, a nonempty lesson ID and
title, a `params` object, a `bounds` object with three-component `center`/`size`,
and a nonempty `primitives` list. Metrics and insights may accompany the sample.

| Sample primitive | Native representation | Preserved meaning |
|---|---|---|
| `line` with ordered `points` | `Shape` / `IndexedLineSet` / `Coordinate` | One connected sampled polyline; no interpolation beyond its straight segments |
| `sphere` with `position` and positive `radius` | `Transform` / `Shape` / `Sphere` | A mathematical point marker with an authored visual radius |
| `mesh` with `points` and face `indices` | `Shape` / `IndexedFaceSet` / `Coordinate` | Sampled polygon faces, rendered two-sided; face indexes remain explicit |
| `box` with `position` and positive `size` | `Transform` / `Shape` / `Box` | An authored rectangular sample volume, such as a Riemann rectangle with a small display depth |

Colors are three values in `[0,1]`; optional transparency is in `[0,1]`.
Material and lighting are presentation choices. Lines use their requested color
as emissive color; surfaces use diffuse color with restrained highlights.
The line style requests a scale factor through standard `LineProperties`.
Actual screen line width remains renderer/platform dependent.

The adapter does not emit `Script`, `Inline`, external textures, audio, shader
URLs or a document type declaration. It does not import arbitrary X3D or execute
incoming lesson text. Unsupported primitive kinds are refused, rather than
silently dropping an unfamiliar part of a mathematical picture.

Primitive source IDs are preserved as string metadata. XML `DEF` identifiers
are generated independently as `MathLabPrimitive_0000`, etc., so punctuation,
Unicode or a leading digit in a source ID cannot become XML identifier syntax.
Duplicate source IDs are refused because they would make source correspondence
ambiguous. This version uses no `USE` references or routes to reconstruct.

## Camera and scene framing

Every document contains `WorldInfo`, `Background`, `NavigationInfo`, a named
`Viewpoint` with DEF `MathLabView`, two directional lights and a subtle bounded
reference grid. The first viewpoint frames the declared bounds. Its center of
rotation matches the model center; the default navigation is Examine.

Linear algebra, derivatives, integration and Fourier lessons face the XY plane.
The small depth of integration boxes is a display aid, not a request to tilt
the area diagram. Other planar samples also use a frontal view. Genuinely 3D
samples use a modest oblique camera with a rotation computed to face the center.
Reloading an export restores this authored view; an HTML Home action can replace
the world with the same document.

The grid, lights and camera are bounded display helpers, not additional kernel
samples. No automatic 3D text is added: explanations and legends remain in the
HTML interface, and mathematical/numerical descriptions survive in metadata.
This avoids making a basic geometry export depend on an additional font asset.
An independent X3D viewer can inspect geometry, title, parameters and metrics,
but does not automatically reproduce the HTML teaching sequence.

## Bounded preflight

Validation completes before XML construction. Current limits are application
policy rather than X3D specification limits:

| Quantity | Policy |
|---|---:|
| Mathematical primitives | 1–1,000 |
| Aggregate polyline/mesh coordinate points | At most 25,000 |
| Aggregate mesh face-index entries | At most 150,000 |
| Encoded metadata | At most 65,536 UTF-8 bytes |
| Absolute input numeric value | At most 100,000,000, finite |

Every vector has exactly three components; booleans are not accepted as numbers.
Dimensions are nonnegative for bounds, with at least one positive dimension.
Sphere radius and every box dimension must be positive. Color and transparency
have their own tighter intervals. Line samples need at least two points.

Face indices must reference existing points or use `-1` as a face separator.
Each face needs at least three distinct indices. An unterminated valid final
face receives its separator. Repeated or empty faces are refused. A face whose
distinct vertices happen to be collinear remains allowed: a singular matrix
can legitimately collapse area, and rejecting that case would erase a key
lesson. Such a collapsed mesh may naturally have no visible filled area.

The caps above concern supplied mathematical geometry. The reference grid adds
one bounded line set with 44 coordinate points. Metadata/provenance and a small
fixed scene wrapper add further nodes. Do not equate the input-primitive count
with a native renderer's draw-call count.

## Provenance and numerical boundaries

One `MetadataString` on `WorldInfo` contains canonical JSON with adapter version,
sample schema, lesson, exact parameters, metrics, insights and declared bounds.
It also stores two SHA-256 identities:

- `configuration_sha256` identifies canonical lesson ID and parameter JSON.
- `sample_sha256` identifies the complete canonical pre-export sample, including
  geometry and numerical diagnostics. It distinguishes changed kernel output
  even when lesson parameters remain identical.

These hashes identify consumed data, not an authenticated publisher, signed
lesson, independent proof or complete source-code identity. A reproducibility
record should retain the kernel/adapter code identity and executor as well.
The final XML file has its own byte identity, recorded by the release builder.

MFString quote/backslash escaping and XML attribute escaping are separate steps.
The adapter handles both, so text such as `a "quoted" <curve>` remains text.
XML 1.0 control characters are refused. Primitive metadata appears before
Appearance and geometry to satisfy Shape's XML content order. An initial actual
XSD probe caught the opposite order; the repaired order has a retained control.

Coordinates are formatted with seventeen significant decimal digits so their
incoming Python binary64 values can round-trip through decimal text. Native
`Coordinate` uses the X3D single-precision field domain; GPU and renderer
representation may round further. Numerical metrics remain the Python model's
calculations. A visual mesh is therefore neither an exact analytic surface nor
an independent numerical verifier.

A stored sample/export is a static mathematical picture. It contains no live
HTML controller, arbitrary lesson program, browser camera gesture history or
complete animation checkpoint. Shared parameters can regenerate another sample
or a Manim explanation through their declared adapters; that is a useful bridge,
not a claim that the two renderers are pixel-equivalent.

## Evidence and limits

`tests/test_x3d.py` contains eighteen standard-library controls for all four
primitive mappings, deterministic output, input preservation, metadata identity,
XML/MFString escaping, generated DEFs, finite ranges, index references, positive
geometry, planar/deep cameras, budgets and refusal paths. The ordering control
specifically guards the XSD defect found during implementation.

These unit controls parse XML and inspect the mapping. They do not claim XSD
conformance, native browser rendering, a hardware performance budget or mathematical
truth by themselves. The parent release run separately validates generated
lesson documents against its pinned schema/implemented semantic instrument and
records actual browser observations. See the release validation record for its
measured scope; an unexecuted stage must remain unexecuted.

Useful next increments are camera/layout overrides in lesson cards, optional
standard-node labels with a retained font closure, native picking with stable
source correspondence, and typed animation channels. Preserve this separation
of model, sample, export, renderer and teaching policy as those features grow.

## Primary technical references

- [X3D 4.0 schema documentation](https://www.web3d.org/specifications/X3dSchemaDocumentation4.0/x3d-4.0.html)
- [IndexedFaceSet schema content](https://www.web3d.org/specifications/X3dSchemaDocumentation4.0/x3d-4.0_IndexedFaceSet.html)
- [MetadataString and its MFString field](https://www.web3d.org/specifications/java/javadoc/org/web3d/x3d/jsail/Core/MetadataString.html)
- [X_ITE Viewpoint tutorial](https://create3000.github.io/x_ite/tutorials/controlling-the-viewpoint/)
- [X_ITE NavigationInfo reference](https://create3000.github.io/x_ite/components/navigation/navigationinfo/)
