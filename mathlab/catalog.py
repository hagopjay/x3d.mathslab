"""Authored lesson contracts. Bounds are part of the experiment, not decoration."""
from copy import deepcopy
from math import pi


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


def catalog():
    """Return an independent JSON-safe copy so callers cannot alter validation policy."""
    return deepcopy(_LESSONS)


def lesson_spec(lesson_id):
    for lesson in _LESSONS:
        if lesson["id"] == lesson_id:
            return deepcopy(lesson)
    raise ValueError("Unknown lesson: " + str(lesson_id))
