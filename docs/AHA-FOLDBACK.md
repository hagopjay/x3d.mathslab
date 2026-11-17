# Aha Atlas: findings to fold back

This iteration extends `hagopjay/x3d.mathslab` at commit
`24c9bbd8ad92e477c56f239476cd3dff7c05ecb2`. It doubles the collection to twelve
lessons and adds guided presets, preparation filters, color legends, study
resources, and a worked learner atlas. It remains an X3D-first sampled
mathematics laboratory with optional Manim source export.

## Educational findings embodied in code

| Design choice | Concrete lesson | Portable implication |
|---|---|---|
| Hold an invariant fixed to expose shape. | Standardized binomial laws retain variance one as n grows. | Show what a transformation removes before interpreting what remains. |
| Show a resistant case beside a successful one. | Thirty rare Bernoulli trials remain skewed; a symmetric pair of outcomes is not a bell curve. | A named counterexample is often more useful than a larger parameter range. |
| Keep reference, approximation, and bound distinct. | Taylor's actual error ribbon differs from its rigorous pointwise remainder bracket. | Name exactly what each diagnostic measures. |
| Distinguish a material object from a measuring boundary. | Moving tracer ring versus fixed integration circle. | Coincident geometry can otherwise suggest an incorrect identity. |
| Change coordinates without changing the reachable set. | Nearly parallel columns preserve a plane but enlarge least-squares coefficients. | A stable picture can coexist with sensitive numerical coordinates. |
| Separate instantaneous state from persistent structure. | A flat standing wave can have maximal kinetic energy; permanent nodes stay zero. | Ask about a time interval before inferring structure from one frame. |
| Expose special cases and their scope. | Roots of unity and primitive closure; a linear source/rotation field. | A clean exact model works best when its special assumptions remain visible. |

These are design hypotheses and implementation observations. No study of student
learning, retention, accessibility, or engagement was conducted.

## Architecture learned from the extension

The original six builders remain in `kernel.py`. Two bounded extensions export
authored `LESSONS` and renderer-neutral `MODELS`. Builders import the existing
geometry helpers at evaluation time, preventing a catalog import cycle. They
use only Python's standard library and enter the existing Pyodide installation
list. The catalog owns control domains, schema, presets and collection metadata.

Producer identities now include both extension modules. Omitting them would
allow a running server to identify old in-memory mathematics with new disk
bytes. The restart-on-source-change rule therefore covers every model.
Reproducibility hashes still identify bytes within one runtime; cross-runtime
floating-point comparisons require tolerances.

View intent is now model data: `planar` or `spatial`. Native X3D, SVG projection
and baked Manim source consume it. A lesson-name whitelist would have silently
flattened the new projection lesson. Older external samples retain the
adapter's automatic framing fallback.

Presets merge partial configurations with defaults, explain the intended
observation, and recompute through the normal request gate. Slider changes clear
the preset indication. Every preset is validated and round-tripped through X3D
metadata recovery in the curriculum test.

## Representation findings

- Probability bars have width Δz and mathematical height P(K=k)/Δz. Bars and
  normal density share a declared display factor six; displayed bar area divided
  by six equals mass. Undrawn tail mass is reported; all outcomes remain in data.
- Standing-wave lanes have explicit vertical/depth offsets. Mathematical arrays
  retain unshifted displacements. Time is a fraction of period; speed changes
  physical period while leaving a fixed normalized phase unchanged.
- Complex interpolation chooses one angle path. Fractional powers are a display
  path, not a single-valued global complex power convention. The root polygon
  represents roots of unity, not arbitrary complex-root solving.
- Least-squares geometry uses the known QR basis. Huge opposing coefficient
  vectors are omitted; coefficients and condition number remain in measurements.
- X3D and Manim exports are static samples. Controls and predictions live in the
  browser and parameter cards; source export is not an interactive replay.

## Bounded next iterations

1. **SVD as a bridge:** stage Vᵀ, Σ, U; connect matrices, conditioning, rank
   truncation and image compression. Check orthogonality and reconstruction.
2. **Weighted and noisy fits:** introduce deterministic synthetic observations
   and show how a metric changes perpendicularity. Use QR/SVD for computation.
3. **Vector fields beyond circles:** add nonuniform fields and polygonal
   boundaries so refinement becomes a genuine numerical experiment.
4. **Research notebook:** compare two retained cards, save a revised explanation,
   and export an observation record. Evaluate unseen transfer with educators.

Each next iteration should add a mathematical reference, a surprising boundary
case, and a representation contract before adding visual complexity.
