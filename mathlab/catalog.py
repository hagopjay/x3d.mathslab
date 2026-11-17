"""Authored lesson contracts. Bounds are part of the experiment, not decoration."""
from copy import deepcopy
from math import pi

from .lessons_analysis import LESSONS as ANALYSIS_LESSONS
from .lessons_structures import LESSONS as STRUCTURE_LESSONS
from .lessons_inference import LESSONS as INFERENCE_LESSONS
from .lessons_science import LESSONS as SCIENCE_LESSONS


def _p(key, label, lo, hi, step, default, unit="", integer=False):
    return {"id": key, "label": label, "min": lo, "max": hi, "step": step,
            "default": default, "unit": unit, "type": "integer" if integer else "number"}


_LESSONS = [
    {"id": "linear", "title": "The Shape of a Matrix", "tagline": "Move a whole space with four numbers.",
     "accent": "#73dfff", "formula": "B(t) = (1 − t)I + tA    ·    signed area factor = det B",
     "description": "Watch the grid, basis arrows and unit circle transform together. An eigenvector keeps its line; it need not keep its length or direction.",
     "parameters": [_p("a", "Matrix a", -2.5, 2.5, .05, 1.2), _p("b", "Matrix b", -2.5, 2.5, .05, .6),
                    _p("c", "Matrix c", -2.5, 2.5, .05, .2), _p("d", "Matrix d", -2.5, 2.5, .05, .9),
                    _p("blend", "Transformation progress", 0, 1, .01, 1)],
     "animation": {"parameter": "blend", "min": 0, "max": 1, "speed": .22, "mode": "pingpong"},
     "story": [{"title": "Predict", "text": "Read the two columns of A as the destinations of the horizontal and vertical basis vectors."},
               {"title": "Transform", "text": "Sweep progress from zero to one. The cyan grid is B(t); the quiet grid is the original space."},
               {"title": "Explain", "text": "A negative determinant reverses orientation. A zero determinant collapses area. Real eigenvectors retain their line; some matrices have no real eigendirections."}],
     "challenge": {"question": "Can a matrix reverse orientation without changing the magnitude of area?", "answer": "Yes. Try a=−1, b=c=0, d=1: det A=−1, so areas retain magnitude and orientation reverses."}},
    {"id": "derivative", "title": "A Secant Becomes a Tangent", "tagline": "A derivative is a limit you can investigate.",
     "accent": "#ffc976", "formula": "f(x)=sin x+0.15x²    ·    f′(x)=cos x+0.3x",
     "description": "Shrink a finite interval and compare forward and central slopes with a known analytic derivative. Small h changes approximation error; it does not turn a sample into a proof.",
     "parameters": [_p("x", "Point x", -2.5, 2.5, .02, .7), _p("h", "Step h", .005, 1.5, .005, .6)],
     "story": [{"title": "Predict", "text": "The amber secant connects x and x+h. Predict whether it is steeper than the tangent."},
               {"title": "Approach", "text": "Reduce h. Compare a one-sided difference with a symmetric central difference."},
               {"title": "Check", "text": "The analytic derivative is an independent reference. Here the central-difference error is at most h²/6 because |f‴|≤1."}],
     "challenge": {"question": "Does halving h usually halve the central-difference error?", "answer": "For this smooth function away from cancellation effects, central error is order h²: halving h typically reduces it by about four, not two."}},
    {"id": "integral", "title": "Build an Area from Samples", "tagline": "Finite rectangles; an exact reference.",
     "accent": "#8affcf", "formula": "f(x)=0.25x²+0.35cos(2x)+1.2    ·    Σ f(xᵢ*)Δx",
     "description": "Move the interval, change the rectangle count and compare left, midpoint and right sampling. The curve stays positive on this lesson's domain, so the signed integral is also geometric area.",
     "parameters": [_p("a", "Lower limit a", -3, 0, .05, -2), _p("b", "Upper limit b", .2, 3, .05, 2),
                    _p("n", "Rectangle count", 1, 64, 1, 12, integer=True),
                    _p("sample", "Sample: −1 left · 0 midpoint · 1 right", -1, 1, 1, 0, integer=True)],
     "story": [{"title": "Assemble", "text": "Each mint rectangle has width Δx and height determined by its sample position."},
               {"title": "Compare", "text": "The exact reference uses F(x)=x³/12+0.175sin(2x)+1.2x. Read approximation minus reference as signed error."},
               {"title": "Bound", "text": "On this domain |f″|≤1.9. The midpoint error bound is 1.9(b−a)³/(24n²); it does not apply to left/right sampling."}],
     "challenge": {"question": "Must a right-endpoint sum overestimate this curve?", "answer": "No. That rule requires an increasing function on the whole interval; this curve changes monotonicity. Inspect the actual signed error."}},
    {"id": "fourier", "title": "A Wave Made of Circles", "tagline": "Circular motion composes a square-wave approximation.",
     "accent": "#e7a5ff", "formula": "Sₙ(θ) = (4/π) Σₖ₌₀ⁿ⁻¹ sin((2k+1)θ)/(2k+1)",
     "description": "An epicycle chain and a waveform share one phase. More odd harmonics improve average accuracy while ringing remains near the jumps.",
     "parameters": [_p("terms", "Odd harmonics", 1, 12, 1, 5, integer=True), _p("phase", "Phase θ", 0, 2*pi, .02, .9, "rad")],
     "animation": {"parameter": "phase", "min": 0, "max": 2*pi, "speed": .75, "mode": "loop"},
     "story": [{"title": "Compose", "text": "Every circle contributes one rotating vector. Its vertical component is one sine term."},
               {"title": "Link", "text": "The final circle endpoint and the amber dot on the wave have exactly the same vertical sum."},
               {"title": "Distinguish", "text": "The RMS error is a whole-period quantity. It can fall while the largest overshoot near a discontinuity remains noticeable. At a jump the symmetric series converges to the midpoint."}],
     "challenge": {"question": "Can the RMS error improve while a visible overshoot remains?", "answer": "Yes. Ringing narrows around a jump as terms increase. A smaller average error does not mean uniform pointwise accuracy at the discontinuity."}},
    {"id": "lorenz", "title": "Two Almost-Identical Beginnings", "tagline": "A chaotic flow, with its numerical method visible.",
     "accent": "#ff93b9", "formula": "ẋ=σ(y−x),  ẏ=x(ρ−z)−y,  ż=xy−βz",
     "description": "Compare nearby initial conditions and a separate step-size refinement. Neither a butterfly-shaped picture nor one diverging pair proves chaos.",
     "parameters": [_p("sigma", "σ", 5, 16, .2, 10), _p("rho", "ρ", 1, 40, .5, 28),
                    _p("beta", "β", 1, 4, .05, 8/3), _p("dt", "Maximum RK4 step", .005, .03, .001, .01, "s"),
                    _p("duration", "Integration duration", 2, 20, .5, 20, "s"),
                    _p("separation", "Initial x separation", .000001, .1, .0001, .001)],
     "story": [{"title": "Separate causes", "text": "The pink and cyan trajectories use the same method and step, but start with slightly different x values."},
               {"title": "Refine", "text": "The numerical diagnostic compares the base trajectory's endpoint against an h/2 integration from the same initial state."},
               {"title": "Interpret", "text": "Sensitivity to initial data and finite-step error are different questions. Long-time endpoint differences can amplify both; this is not a rigorous error bound or a Lyapunov-exponent estimate."}],
     "challenge": {"question": "If two curves separate, have you measured numerical error?", "answer": "Only if the initial state is held fixed and the numerical method or step is varied. The nearby-start pair intentionally changes initial data instead."}},
    {"id": "gradient", "title": "Find the Floor of a Valley", "tagline": "Learning rate meets curvature.",
     "accent": "#a5b7ff", "formula": "f=½(u²+κv²),  [u,v]ᵀ=Rᵀ[x,y]ᵀ    ·    pₖ₊₁=pₖ−α∇f(pₖ)",
     "description": "Follow gradient descent on a rotated positive-definite quadratic. The surface is known, the minimum is known, and the exact linear recurrence supplies a reference.",
     "parameters": [_p("rate", "Learning rate α", .01, .28, .005, .15), _p("condition", "Curvature ratio κ", 1, 20, .5, 8),
                    _p("start_x", "Starting x", -2.5, 2.5, .1, 2.2), _p("start_y", "Starting y", -2.5, 2.5, .1, 1.6),
                    _p("steps", "Descent steps", 1, 60, 1, 28, integer=True)],
     "story": [{"title": "Read the valley", "text": "The two Hessian eigenvalues are 1 and κ. Rotation changes the direction of the valley, not those eigenvalues."},
               {"title": "Choose a step", "text": "A mode of curvature λ is multiplied by 1−αλ per step. A negative factor zigzags; magnitude above one amplifies that mode."},
               {"title": "Verify", "text": "Every start converges precisely when 0<α<2/κ. The exact eigen-coordinate recurrence checks the numerical iteration. Iterates outside the displayed domain remain in numeric data but are omitted from the scene."}],
     "challenge": {"question": "Can a larger learning rate make convergence slower or unstable?", "answer": "Yes. Compare max(|1−α|,|1−ακ|). As it approaches one convergence slows; above one some modes grow. Reducing α is not always faster either."}},
]


_ENRICHMENTS = {
    "linear": {
        "level": "Grade 10–12", "prerequisites": ["Coordinates", "Vectors"],
        "resources": [{"title": "3Blue1Brown · Linear transformations and matrices",
                       "url": "https://www.3blue1brown.com/lessons/linear-transformations/",
                       "note": "See matrix columns as destinations of basis vectors; then test a reflection here."}],
        "presets": [
            {"title": "Mirror without shrinking", "params": {"a": -1, "b": 0, "c": 0, "d": 1}, "why": "Signed area reverses while its magnitude stays one."},
            {"title": "Collapse a dimension", "params": {"a": 1, "b": 2, "c": .5, "d": 1}, "why": "Dependent columns turn a square into a line."},
            {"title": "Rotate with no real eigenline", "params": {"a": 0, "b": -1, "c": 1, "d": 0}, "why": "A quarter turn preserves area and has no real eigendirection."}],
        "legend": [{"label": "Transformed grid", "color": "#47d6ff"}, {"label": "Circle image", "color": "#ffba52"}, {"label": "Real eigenlines", "color": "#a68cff"}]},
    "derivative": {
        "level": "Grade 10–12", "prerequisites": ["Functions", "Slope", "Radians"],
        "resources": [{"title": "OpenStax Calculus 1 · Defining the derivative", "url": "https://openstax.org/books/calculus-volume-1/pages/3-1-defining-the-derivative", "note": "Connect the secant-slope limit with tangent and instantaneous rate."}],
        "presets": [
            {"title": "A wide secant", "params": {"x": .7, "h": 1.2}, "why": "Start with a visible interval before taking a limit."},
            {"title": "A close look", "params": {"x": .7, "h": .02}, "why": "Compare forward and symmetric differences at the same point."}],
        "legend": [{"label": "Function", "color": "#47d6ff"}, {"label": "Secant", "color": "#ffba52"}, {"label": "Analytic tangent", "color": "#ff59a8"}]},
    "integral": {
        "level": "Grade 10–12", "prerequisites": ["Functions", "Area", "Finite sums"],
        "resources": [{"title": "OpenStax Calculus 1 · The definite integral", "url": "https://openstax.org/books/calculus-volume-1/pages/5-2-the-definite-integral", "note": "Riemann sums approach signed accumulation; this particular curve is positive."}],
        "presets": [
            {"title": "Coarse midpoint", "params": {"n": 4, "sample": 0}, "why": "Compare the finite sum with the exact antiderivative."},
            {"title": "Refined midpoint", "params": {"n": 32, "sample": 0}, "why": "Test the n⁻² error bound with all other inputs fixed."}],
        "legend": [{"label": "Function", "color": "#ffba52"}, {"label": "Sampled rectangles", "color": "#5cffba"}, {"label": "Sample locations", "color": "#ff59a8"}]},
    "fourier": {
        "level": "Undergraduate 1", "prerequisites": ["Trigonometry", "Radians", "Finite sums"],
        "resources": [{"title": "3Blue1Brown · But what is a Fourier series?", "url": "https://www.3blue1brown.com/lessons/fourier-series/", "note": "Study rotating vectors, then distinguish whole-period error from ringing near jumps."}],
        "presets": [
            {"title": "One harmonic", "params": {"terms": 1}, "why": "Find the single sine inside a rotating vector."},
            {"title": "Many harmonics, persistent ringing", "params": {"terms": 12, "phase": .12}, "why": "More terms improve RMS error without removing the Gibbs phenomenon."}],
        "legend": [{"label": "Circles", "color": "#a68cff"}, {"label": "Rotating vectors", "color": "#5cffba"}, {"label": "Partial sum", "color": "#47d6ff"}, {"label": "Square-wave plateaus", "color": "#1f4063"}]},
    "lorenz": {
        "level": "Undergraduate 2–3", "view": "spatial", "prerequisites": ["Differential equations", "Numerical integration"],
        "resources": [{"title": "MIT · Lorenz attractor and chaos", "url": "https://ocw.mit.edu/courses/res-18-009-learn-differential-equations-up-close-with-gilbert-strang-and-cleve-moler-fall-2015/resources/lorenz-attractor-and-chaos/", "note": "Strang and Moler introduce deterministic sensitivity; compare initial-data changes with step refinement here."}],
        "presets": [
            {"title": "Short horizon", "params": {"duration": 4}, "why": "Nearby starts initially remain nearby."},
            {"title": "A longer horizon", "params": {"duration": 20}, "why": "Separate initial-data sensitivity from numerical step-size sensitivity."}],
        "legend": [{"label": "Base trajectory", "color": "#47d6ff"}, {"label": "Nearby start", "color": "#ff59a8"}]},
    "gradient": {
        "level": "Undergraduate 2–3", "view": "spatial", "prerequisites": ["Gradients", "Eigenvalues", "Quadratics"],
        "resources": [{"title": "Boyd and Vandenberghe · Convex Optimization", "url": "https://web.stanford.edu/~boyd/cvxbook/", "note": "Chapter 9 connects gradient descent with curvature and convergence."}],
        "presets": [
            {"title": "Round bowl", "params": {"condition": 1, "rate": .2}, "why": "Equal curvatures contract both modes equally."},
            {"title": "Zigzag, yet converge", "params": {"condition": 8, "rate": .2}, "why": "A negative mode factor alternates sign while its magnitude stays below one."},
            {"title": "Cross the stability boundary", "params": {"condition": 8, "rate": .26}, "why": "The steep mode amplifies when α exceeds 2/κ."}],
        "legend": [{"label": "Quadratic surface", "color": "#a68cff"}, {"label": "Descent iterates", "color": "#ffba52"}, {"label": "Minimum", "color": "#ff59a8"}]},
}
for _lesson in _LESSONS:
    _lesson.update(_ENRICHMENTS[_lesson["id"]])
_LESSONS.extend(ANALYSIS_LESSONS + STRUCTURE_LESSONS + INFERENCE_LESSONS + SCIENCE_LESSONS)

# Coordinate meanings and conceptual bridges remain catalog data, so every
# lesson uses the same UI and exporters without a browser-side subject switch.
_BRIDGES = {
    "linear": ("XY plane: original and transformed Cartesian coordinates.", [
        ("svd", "Decompose a transformation into two rotations and independent stretches."),
        ("least_squares", "A column space is the set a matrix can reach.")]),
    "derivative": ("Horizontal: x. Vertical: f(x). Slopes use the unscaled mathematical coordinates.", [
        ("taylor", "A tangent is the first-order Taylor approximation."),
        ("refraction", "A zero travel-time derivative selects the crossing point.")]),
    "integral": ("Horizontal: x. Vertical: f(x). Rectangle area represents f(x*) Δx.", [
        ("probability", "Probability density becomes probability through area."),
        ("heat", "Integrate temperature to distinguish total heat from roughness.")]),
    "fourier": ("Left: rotating vectors in a plane. Right: phase θ horizontally, partial-wave value vertically.", [
        ("aliasing", "A continuous frequency and its sampled identity are different information."),
        ("heat", "Diffusion damps each Fourier mode at a rate proportional to frequency squared.")]),
    "lorenz": ("Display: (0.36x, 0.36(z−23), 0.36y); vertical height represents the Lorenz z coordinate.", [
        ("vector_field", "Start with an exactly solvable flow before a nonlinear numerical flow."),
        ("gradient", "Compare an attracting optimization recurrence with a continuous dynamical system.")]),
    "gradient": ("Display: (x, 0.6f(x,y)/√κ, y). Metric losses retain mathematical units.", [
        ("lagrange", "A constraint changes which downhill directions are available."),
        ("svd", "Unequal stretch factors explain conditioning and narrow optimization valleys.")]),
    "complex": ("Horizontal: real part. Vertical: imaginary part. Amber interpolates successive powers along one chosen angle path.", [
        ("fourier", "Rotating complex vectors can be added to build a signal."),
        ("svd", "Complex multiplication scales every direction equally; general matrix stretches need not.")]),
    "taylor": ("Horizontal: x within [a−R,a+R]. Vertical: sine/polynomial value; the bracket shows a pointwise bound.", [
        ("derivative", "Local slope agreement is the first derivative-matching condition."),
        ("refraction", "Local derivatives can locate a global minimum when strict convexity is known.")]),
    "waves": ("Horizontal: x−3 for string position x∈[0,6]. Wave lanes offset vertically ±2.7; middle is the sum. Time is t/T.", [
        ("heat", "The same spatial modes oscillate in a wave equation but decay in a heat equation."),
        ("aliasing", "A finite sequence of snapshots can disguise oscillation frequency.")]),
    "probability": ("Horizontal: standardized count Z. Vertical: density ×6; displayed bar area divided by six equals probability mass.", [
        ("bayes", "A distribution and a probability conditional on evidence answer different questions."),
        ("integral", "A normal density gives probability through area, not curve height.")]),
    "least_squares": ("Spatial coordinates: mathematical (x,y,z). Orbit to separate the target, plane and perpendicular residual.", [
        ("svd", "Singular values explain why nearly dependent columns produce fragile coefficients."),
        ("gradient", "The closest-point problem can also be viewed as minimizing a quadratic.")]),
    "vector_field": ("XY plane: field positions. Cyan velocities use common scale 0.28; the integration circle stays fixed while tracers move.", [
        ("lorenz", "Replace this exact linear flow with a nonlinear numerically integrated field."),
        ("heat", "Flux connects local differential laws with changes across a whole domain.")]),
}
for _lesson in _LESSONS:
    if _lesson["id"] in _BRIDGES:
        _axes, _links = _BRIDGES[_lesson["id"]]
        _lesson["axes"] = _axes
        _lesson["connections"] = [{"lesson": key, "why": why} for key, why in _links]


def catalog():
    """Return an independent JSON-safe copy so callers cannot alter validation policy."""
    return deepcopy(_LESSONS)


def lesson_spec(lesson_id):
    for lesson in _LESSONS:
        if lesson["id"] == lesson_id:
            return deepcopy(lesson)
    raise ValueError("Unknown lesson: " + str(lesson_id))
