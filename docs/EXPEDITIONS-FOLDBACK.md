# Insight Expeditions: six new bridges

This edition extends the twelve-lesson Aha Atlas to eighteen lessons and fifty
guided presets. All new models use standard-library Python, the existing
bounded geometry contract, the same parameter-card schema generator, native
X3D export, and optional baked Manim source generation.

## What the new experiments make visible

| Experiment | Deliberately revealing case | Mathematical insight |
|---|---|---|
| SVD | Equal singular values, then an exactly zero second value | A preferred basis can lose uniqueness; a map can lose information. These are distinct events. |
| Bayes | Same detector, rarer tag | Conditioning changes the denominator. Detector sensitivity is not the posterior probability. |
| Lagrange multipliers | Nonzero objective gradient at the constrained maximum | Only feasible tangent derivatives must vanish. Unconstrained stationarity is a different requirement. |
| Aliasing | A 7 Hz cosine sampled at 8 Hz | An infinite family of continuous signals can share the same samples. A recovery assumption supplies information the samples omit. |
| Heat | High-frequency ripples decay while a broad cosine remains | A spatial second derivative becomes a frequency-squared damping rate. Mean and squared fluctuation behave differently. |
| Refraction | Slower lower medium with a movable crossing | Travel-time optimization can choose a geometrically longer path. Differentiation yields Snell's law. |

The six lessons share the prediction→controlled change→explanation→transfer
rhythm. Three primary questions guide each: which quantity is represented,
what assumption licenses the reference calculation, and which change would
break a naive explanation? Source links support further study; the authored
geometry and prose are original teaching adaptations.

## Technical findings carried into the implementation

**Representation should travel with the model.** Every lesson now declares a
coordinate caption. UI captions explain chart scales and offsets; exported
sample/X3D metadata retains the same description. This matters for conditional
Bayes zooms, separated SVD panels, a heat sheet whose depth is time, and a
refraction inset whose horizontal coordinates differ from the ray diagram.

**Preserve small probabilities exactly.** The Bayes mosaic uses areas rather
than rounded tiles. Expected counts for 10,000 objects can be fractional. The
positive-only panel declares its independent conditional normalization. This
keeps the rare-event example mathematically faithful even when the original
tagged strip is visually thin.

**Parameterize a clean family and disclose its scope.** SVD is constructed as
R(u)ΣR(v)ᵀ; it demonstrates factor action without requiring a numerical solver.
It covers an orientation-preserving family, including rank-one boundaries.
General real SVD permits orthogonal reflections too. Target singular values
remain separate from the matrix currently shown during the staged animation.

**Independent references need different routes to the result.** Refraction
uses derivative bisection; the independent instrument uses bounded minimization.
Ellipse extrema use a closed-form support function; a separate optimizer
investigates the parameterized curve. SVD checks compare singular values and
matrix identities rather than insisting on a unique singular-vector sign.

**A limiting theorem is information with assumptions.** The aliasing lesson
exhibits exact sample equality. A known strict bandlimit is a separate premise
for ideal reconstruction. It avoids inferring arbitrary continuous signals
from a finite two-second record, and keeps signed alias frequency with its
phase convention instead of silently folding a sign away.

**Use exact solutions to teach numerical judgment.** Heat has an exact two-mode
solution, an independent periodic quadrature of mean/squared fluctuation, and a
finite-difference PDE diagnostic whose nonzero residual is discretization error.
This is a controlled comparison, not an arbitrary PDE solver. Its 25×49 history
sheet stays within the existing Manim face budget.

**Layout needs adversarial mathematical cases.** Independent review found that
a fixed refraction inset baseline could let the cost graph overlap physical
rays at high contrast. The baseline is now derived from the maximum plotted
cost and target depth, keeping the graph below the physical diagram while
preserving unscaled cost differences. A regression test covers the extreme.

The guide links exposed another integration seam: static hosting uses `/web/`,
while the local app originally served only `/`. The loopback server now also
serves the `/web/` alias and its assets, so the same relative study links work
in both layouts. An HTTP regression checks the guide, alias, script and README.

## Connected learning rather than a longer menu

Catalog-authored connection buttons name a specific bridge and retain the
current reading tab. Following a connection reveals a destination hidden by
filters and moves keyboard focus to its heading. Invalid, self and duplicate
destinations are omitted. Tests exercise those behaviors with the actual UI
functions. Connections remain recommendations, not a claimed mastery model.

The optional preview renderer projects actual model primitives into a contact
sheet and records source hashes in its PNG metadata. It provides a reproducible
view of geometry without claiming native X_ITE pixels or GPU performance.

## Next research questions

The worked guide proposes transfer problems rather than judging understanding
from slider activity. Useful follow-up comparisons include whether paired
wave/heat scenes distinguish oscillation from smoothing; whether an area-based
Bayes explanation transfers to a fresh detector; and whether students can state
the recovery premise missing from an aliasing example. No learner study has
been conducted, and these questions remain hypotheses for testing.
