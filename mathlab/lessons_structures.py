"""Probability, projection and vector-calculus lessons with explicit references.

These models use only the standard library, including in the Pages runtime.
Geometry is sampled; numerical arrays retain the declared mathematical units.
Kernel helpers are imported at call time to keep catalog construction acyclic.
"""
from math import comb, cos, erf, exp, fsum, pi, sin, sqrt


def _p(key, label, lo, hi, step, default, unit="", integer=False):
    return {"id": key, "label": label, "min": lo, "max": hi, "step": step,
            "default": default, "unit": unit, "type": "integer" if integer else "number"}


LESSONS = [
    {"id": "probability", "title": "A Bell Curve from Coin Counts",
     "shortName": "Probability becomes a bell", "domain": "PROBABILITY & LIMITS",
     "level": "Grade 10–12",
     "prerequisites": ["Binomial coefficients", "Mean and variance", "Graph area"],
     "accent": "#8affcf", "tagline": "Exact discrete probabilities meet a continuous limit.",
     "formula": "K ∼ Binomial(n,p)    ·    Z=(K−np)/√(np(1−p))    ·    Z ⇒ N(0,1)",
     "description": "Change the number of independent, identically distributed Bernoulli trials. The mint bars are exact binomial probabilities divided by their standardized width; the amber curve is the standard normal density. Both density heights are displayed ×6. Standardizing keeps mean zero and variance one, exposing shape rather than shrinking spread.",
     "parameters": [_p("n", "Independent trials n", 1, 80, 1, 12, integer=True),
                    _p("p", "Success probability p", .05, .95, .01, .35)],
     "story": [{"title": "Predict the shape", "text": "Set n=1. There are only two possible counts, even though the normal curve is continuous. Ask whether symmetry and a bell shape are the same property."},
               {"title": "Standardize, then grow", "text": "Increase n while holding p fixed. Each possible count becomes z=(k−np)/√(np(1−p)); the standardized spacing shrinks while the variance stays one."},
               {"title": "Find a resistant case", "text": "Set p=0.05. Rare successes retain visible skew at sizes that look almost normal for p=0.5. The CLT is a limiting statement, not a promise for n=30."}],
     "challenge": {"question": "Does doubling n halve the standardized distribution's variance?",
                   "answer": "No. Z has variance exactly one for every allowed n and p. The unstandardized sample average has variance p(1−p)/n. Standardization lets us compare shape on a common scale."},
     "presets": [{"title": "Only two outcomes", "params": {"n": 1, "p": .5}, "why": "Symmetry alone does not create a bell curve."},
                 {"title": "The shape emerges", "params": {"n": 80, "p": .5}, "why": "Many independent contributions make the density-scaled bars follow the normal curve."},
                 {"title": "Rare-event resistance", "params": {"n": 30, "p": .05}, "why": "The same sample size can retain pronounced skew when success is rare."}],
     "legend": [{"label": "Exact probability ÷ bin width (height ×6)", "color": "#5cffba"},
                {"label": "Standard normal density (height ×6)", "color": "#ffba52"}],
     "resources": [{"title": "OpenStax: The Central Limit Theorem for Sample Means",
                    "url": "https://openstax.org/books/introductory-statistics-2e/pages/7-1-the-central-limit-theorem-for-sample-means-averages",
                    "note": "Relate the standardized sum to the shrinking standard error of a sample average."}]},
    {"id": "least_squares", "title": "The Closest Reachable Point",
     "shortName": "Least squares as a shadow", "domain": "LINEAR ALGEBRA & INVERSE PROBLEMS",
     "level": "Undergraduate 1", "view": "spatial",
     "prerequisites": ["Vectors in three dimensions", "Dot products", "Linear combinations"],
     "accent": "#ffc976", "tagline": "A residual becomes perpendicular at the best fit.",
     "formula": "minₓ ||Ax−b||²    ·    p=A x̂    ·    Aᵀ(b−p)=0",
     "description": "Two independent columns span a tilted plane in three dimensions. The mint point is the closest reachable point to b. Make the columns nearly parallel: the plane and projection stay fixed, while the coefficients become sensitive. A geometric QR construction supplies the displayed solution.",
     "parameters": [_p("bx", "Target b: x", -2.5, 2.5, .1, 1.4),
                    _p("by", "Target b: y", -2.5, 2.5, .1, 1.2),
                    _p("bz", "Target b: z", -2.5, 2.5, .1, 2.1),
                    _p("tilt", "Plane tilt θ", -1.2, 1.2, .02, .55, "rad"),
                    _p("epsilon", "Column independence ε", .05, 1, .01, .55)],
     "story": [{"title": "Predict the shadow", "text": "The amber vector ends at b. Its mint shadow p must lie in the translucent plane. The pink segment e=b−p is the part the two columns cannot explain."},
               {"title": "Read perpendicularity", "text": "At the best fit, e is perpendicular to both columns. Moving p inside the plane adds an orthogonal error component, so ||b−(p+h)||²=||e||²+||h||²."},
               {"title": "Separate geometry from coordinates", "text": "Reduce ε without moving b or the tilt. The reachable plane is unchanged for ε>0, but large opposing coefficients are needed. The condition number of AᵀA is the square of that of A."}],
     "challenge": {"question": "Can the best-fit point stay fixed while its two coefficients become much larger?",
                   "answer": "Yes. Columns (1,0,0) and (1,ε cos θ,ε sin θ) span the same plane for every ε>0. A fixed component along (0,cos θ,sin θ) needs a coefficient proportional to 1/ε, canceled along x by the other column."},
     "presets": [{"title": "A visible miss", "params": {"bx": 1.4, "by": 1.2, "bz": 2.1, "tilt": .55, "epsilon": 1}, "why": "Read b as a reachable component plus a perpendicular residual."},
                 {"title": "Same shadow, fragile coordinates", "params": {"bx": 1.4, "by": 1.2, "bz": 2.1, "tilt": .55, "epsilon": .05}, "why": "The plane stays fixed while the condition number and opposing coefficients grow."},
                 {"title": "Already reachable", "params": {"bx": 1.4, "by": 1.2, "bz": 0, "tilt": 0, "epsilon": .55}, "why": "A target in the plane has zero residual: least squares becomes an exact solve."}],
     "legend": [{"label": "Target b", "color": "#ffba52"},
                {"label": "Projection p", "color": "#5cffba"},
                {"label": "Residual b−p", "color": "#ff59a8"},
                {"label": "Column a₁", "color": "#47d6ff"},
                {"label": "Column a₂ / reachable plane", "color": "#a68cff"}],
     "resources": [{"title": "MIT 18.06SC: Projection Matrices and Least Squares",
                    "url": "https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/pages/least-squares-determinants-and-eigenvalues/projection-matrices-and-least-squares/",
                    "note": "Connect orthogonal projection, the normal equations, and the geometry of inconsistent systems."}]},
    {"id": "vector_field", "title": "A Source Is Not a Whirlpool",
     "shortName": "Divergence, curl and flow", "domain": "VECTOR CALCULUS & DYNAMICS",
     "level": "Undergraduate 2–3",
     "prerequisites": ["Partial derivatives", "Line integrals", "Parametric circles"],
     "accent": "#e7a5ff", "tagline": "Separate area growth from turning.",
     "formula": "F=(ax−by,bx+ay)    ·    div F=2a    ·    curl_z F=2b",
     "description": "A linear planar velocity field combines a source with rigid rotation. Cyan arrows are uniformly scaled velocities; amber is a fixed integration circle. Mint tracers follow the exact flow exp(at)R(bt), and a pink tracer makes turning visible. Flux and circulation measure different boundary effects.",
     "parameters": [_p("a", "Source strength a", -.5, .5, .02, .2),
                    _p("b", "Rotation rate b", -1.5, 1.5, .05, .8),
                    _p("radius", "Integration circle radius R", .4, 2, .05, 1.3),
                    _p("time", "Tracer time t", 0, 1.5, .02, .8)],
     "animation": {"parameter": "time", "min": 0, "max": 1.5, "speed": .28, "mode": "loop"},
     "story": [{"title": "Split two effects", "text": "Use pure rotation (a=0). A marker turns, but the tracer ring keeps its area and the outward flux is zero. A curved path does not imply a source."},
               {"title": "Follow an area", "text": "Use pure source (b=0). Tracer radii scale by exp(at), so areas scale by exp(2at). The instantaneous fractional area-growth rate is divergence, 2a."},
               {"title": "Walk the boundary", "text": "On the fixed amber circle, outward flux is 2πaR² and counterclockwise circulation is 2πbR². Divide each by πR²: the averages recover divergence and curl_z. In this rigid rotation the angular speed is b, half curl_z."}],
     "challenge": {"question": "Can a field have zero divergence and nonzero curl?",
                   "answer": "Yes: set a=0 and b≠0. The flow is a rigid rotation, preserving area while turning tracers. Conversely b=0 and a≠0 expands or contracts area without turning."},
     "presets": [{"title": "Whirlpool without a source", "params": {"a": 0, "b": 1, "radius": 1.3, "time": 1}, "why": "Nonzero circulation can coexist with zero outward flux."},
                 {"title": "Breathing without turning", "params": {"a": .45, "b": 0, "radius": 1.3, "time": 1}, "why": "Area changes even though the curl vanishes."},
                 {"title": "Spiral into a sink", "params": {"a": -.4, "b": -1, "radius": 1.5, "time": 1.2}, "why": "Negative divergence contracts the ring; negative curl makes the marked tracer turn clockwise."}],
     "legend": [{"label": "Velocity arrows ×0.28", "color": "#47d6ff"},
                {"label": "Fixed integration circle", "color": "#ffba52"},
                {"label": "Advected tracer ring", "color": "#5cffba"},
                {"label": "Marked tracer and its path", "color": "#ff59a8"}],
     "resources": [{"title": "OpenStax Calculus III: Divergence and Curl",
                    "url": "https://openstax.org/books/calculus-volume-3/pages/6-5-divergence-and-curl",
                    "note": "Compare local derivatives with the source and rotation patterns in a vector field."},
                   {"title": "OpenStax Calculus III: Green's Theorem",
                    "url": "https://openstax.org/books/calculus-volume-3/pages/6-4-greens-theorem",
                    "note": "Relate the boundary flux/circulation of the fixed disk to its interior divergence/curl."}]},
]


def _probability(p):
    from .kernel import AMBER, MINT, QUIET, _axes, _line, _metric

    n, probability = p["n"], p["p"]
    mean, variance = n * probability, n * probability * (1 - probability)
    sd = sqrt(variance)
    spacing = 1 / sd
    density_scale = 6.
    probabilities = [comb(n, k) * probability**k * (1-probability)**(n-k)
                     for k in range(n + 1)]
    standardized = [(k-mean)/sd for k in range(n+1)]
    phi = lambda x: exp(-x*x/2)/sqrt(2*pi)
    Phi = lambda x: (1+erf(x/sqrt(2)))/2
    primitives = []
    _axes(primitives, -5, 5, 0, 3)
    for tick in range(-4, 5):
        _line(primitives, f"z_tick_{tick}", [[tick, 0, .01], [tick, -.015, .01]], QUIET)
    shown = []
    for k, (z, mass) in enumerate(zip(standardized, probabilities)):
        if abs(z) > 4.5:
            continue
        height = density_scale*mass/spacing
        # A bar's area divided by density_scale is exactly its probability mass.
        # Both bars and curve use this one declared vertical display transform.
        primitives.append({"kind": "box", "id": f"binomial_{k}",
                           "position": [z, height/2, 0], "size": [spacing, height, .025],
                           "color": MINT[:], "transparency": .2})
        shown.append(k)
    _line(primitives, "normal_density", [[-5+i/40, density_scale*phi(-5+i/40), .055]
                                         for i in range(401)], AMBER)
    cumulative, cdf_errors = 0., []
    for k, mass in enumerate(probabilities):
        cumulative += mass
        cdf_errors.append(abs(cumulative-Phi((k+.5-mean)/sd)))
    total = fsum(probabilities)
    zmean = fsum(z*mass for z, mass in zip(standardized, probabilities))
    zvariance = fsum((z-zmean)**2*mass for z, mass in zip(standardized, probabilities))
    omitted = fsum(mass for k, mass in enumerate(probabilities) if k not in shown)
    return primitives, [
        _metric("mean", "Standardized mean", zmean, "", "The exact finite-n reference is zero; this is its floating-point sum."),
        _metric("variance", "Standardized variance", zvariance, "", "The exact finite-n reference is one, before taking any limit."),
        _metric("mass", "Total discrete probability", total),
        _metric("normal_error", "Max continuity-corrected CDF gap", max(cdf_errors), "", "Measured at k+½ for k=0…n. A finite comparison, not a theorem bound or a density error."),
        _metric("tail", "Undrawn probability mass", omitted, "", "All outcomes remain in numerical data. Only bars with standardized centers |z|≤4.5 are drawn.")
    ], {}, {"n": n, "p": probability, "count_mean": mean, "count_variance": variance,
            "standardized_values": standardized, "probabilities": probabilities,
            "standardized_spacing": spacing, "density_display_scale": density_scale, "standardized_mean": zmean,
            "standardized_variance": zvariance, "total_mass": total,
            "shown_outcomes": shown, "omitted_mass": omitted,
            "max_cc_cdf_gap": max(cdf_errors),
            "skewness": (1-2*probability)/sd}, [
        "Mint bar area divided by 6, not bar height, is probability. Both density heights are displayed ×6 for legibility; horizontal standardized coordinates are unchanged.",
        "The trials are independent and identically distributed Bernoulli(p), with fixed 0<p<1. Their finite, nonzero variance satisfies the classical central limit theorem's assumptions.",
        "Increasing n changes a distribution computed exactly from the binomial formula. This lesson does not estimate it with random samples or claim that a finite n is already normal.",
        "The continuous normal assigns zero probability to an individual point, whereas each finite-n count can have positive mass. Compare areas or CDFs, not point probabilities to curve heights."]


def _least_squares(p):
    from .kernel import AMBER, CYAN, MINT, PINK, QUIET, VIOLET, _line, _metric, _sphere

    bx, by, bz, theta, epsilon = (p[k] for k in ("bx", "by", "bz", "tilt", "epsilon"))
    co, si = cos(theta), sin(theta)
    q1, q2 = [1., 0., 0.], [0., co, si]
    columns = [q1, [1., epsilon*co, epsilon*si]]
    target = [bx, by, bz]
    q = by*co+bz*si
    projected = [bx, q*co, q*si]
    residual = [b-s for b, s in zip(target, projected)]
    coefficients = [bx-q/epsilon, q/epsilon]
    reconstructed = [fsum(columns[j][i]*coefficients[j] for j in range(2)) for i in range(3)]
    normal_rhs = [bx, bx+epsilon*q]
    normal_x2 = (normal_rhs[1]-normal_rhs[0])/(epsilon*epsilon)
    normal_coefficients = [bx-normal_x2, normal_x2]
    lambda_max = (2+epsilon*epsilon+sqrt(4+epsilon**4))/2
    lambda_min = epsilon*epsilon/lambda_max
    condition = sqrt(lambda_max/lambda_min)
    dot = lambda u, v: fsum(a*b for a, b in zip(u, v))
    norm = lambda v: sqrt(dot(v, v))
    orthogonality = [dot(column, residual) for column in columns]
    plane_point = lambda u, v: [u, v*co, v*si]
    primitives = [{"kind": "mesh", "id": "reachable_plane",
                   "points": [plane_point(-4,-4), plane_point(4,-4),
                              plane_point(4,4), plane_point(-4,4)],
                   "indices": [0, 1, 2, 3, -1], "color": VIOLET[:], "transparency": .8}]
    for i in range(-4, 5):
        _line(primitives, f"plane_u_{i}", [plane_point(i,-4), plane_point(i,4)], QUIET)
        _line(primitives, f"plane_v_{i}", [plane_point(-4,i), plane_point(4,i)], QUIET)
    _line(primitives, "target_b", [[0,0,0], target], AMBER)
    _line(primitives, "projection_p", [[0,0,0], projected], MINT)
    _line(primitives, "residual_e", [projected, target], PINK)
    _line(primitives, "column_1", [[0,0,0], columns[0]], CYAN)
    _line(primitives, "column_2", [[0,0,0], columns[1]], VIOLET)
    _sphere(primitives, "target_tip", target, .105, AMBER)
    _sphere(primitives, "projection_tip", projected, .09, MINT)
    _sphere(primitives, "column_1_tip", columns[0], .065, CYAN)
    _sphere(primitives, "column_2_tip", columns[1], .065, VIOLET)
    length = norm(residual)
    if length > 1e-10:
        # A small square in span(q1,e) makes the right angle visible without
        # relying on the camera to make perpendicular vectors look perpendicular.
        side = min(.25, length*.3)
        along = [side*r/length for r in residual]
        c1 = [projected[i]+along[i] for i in range(3)]
        c2 = [c1[i]+side*q1[i] for i in range(3)]
        c3 = [projected[i]+side*q1[i] for i in range(3)]
        _line(primitives, "right_angle", [c1, c2, c3], PINK)
    return primitives, [
        _metric("residual", "Closest distance ||b−p||", length),
        _metric("orthogonality", "Max |aⱼ·(b−p)|", max(map(abs, orthogonality)), "", "Zero is the analytic optimality condition; this is a floating-point diagnostic."),
        _metric("coefficient_1", "Coefficient x̂₁", coefficients[0]),
        _metric("coefficient_2", "Coefficient x̂₂", coefficients[1]),
        _metric("condition", "2-norm condition number κ₂(A)", condition, "", "κ₂(AᵀA)=κ₂(A)². The display solves by the known orthonormal basis rather than forming the normal equations.")
    ], {}, {"columns": columns, "target": target, "projection": projected,
            "residual": residual, "coefficients": coefficients,
            "reconstructed": reconstructed, "orthogonality": orthogonality,
            "residual_norm": length, "condition_A": condition,
            "condition_gram": condition*condition,
            "normal_equation_coefficients": normal_coefficients,
            "normal_equation_coefficient_gap": norm([a-b for a, b in zip(coefficients, normal_coefficients)]),
            "q1": q1, "q2": q2}, [
        "The world uses mathematical coordinates (x,y,z) without flattening. Orbit the camera to see the target, plane, and perpendicular residual.",
        "Columns a₁=(1,0,0) and a₂=(1,ε cos θ,ε sin θ) remain independent because ε≥0.05. Their span is fixed as ε changes, so the projection stays fixed while coordinates can grow.",
        "The mint point uses a stable geometric QR calculation with orthonormal basis q₁=(1,0,0), q₂=(0,cos θ,sin θ). The normal-equation coefficients are retained only as a comparison.",
        "A large condition number describes worst-case sensitivity; it does not say every target has a large error. Drawing the projection directly avoids huge opposing coefficient vectors obscuring its geometry."]


def _arrow(primitives, name, origin, vector, color):
    from .kernel import _line

    dx, dy = vector
    length = sqrt(dx*dx+dy*dy)
    if length < 1e-12:
        return
    x, y = origin
    tip = [x+dx, y+dy, .04]
    head = min(.11, .3*length)
    ux, uy = dx/length, dy/length
    _line(primitives, name, [[x, y, .04], tip], color)
    _line(primitives, name+"_head", [[tip[0]-head*ux-head*.45*uy, tip[1]-head*uy+head*.45*ux, .04],
                                      tip,
                                      [tip[0]-head*ux+head*.45*uy, tip[1]-head*uy-head*.45*ux, .04]], color)


def _vector_field(p):
    from .kernel import AMBER, CYAN, MINT, PINK, QUIET, _axes, _line, _metric, _sphere

    a, b, radius, time = (p[k] for k in ("a", "b", "radius", "time"))
    field = lambda x, y: (a*x-b*y, b*x+a*y)
    flow = lambda theta, t: [radius*exp(a*t)*cos(theta+b*t),
                             radius*exp(a*t)*sin(theta+b*t), .1]
    primitives = []
    _axes(primitives, -2.7, 2.7, -2.7, 2.7)
    for i in range(-2, 3):
        _line(primitives, f"grid_x_{i}", [[i,-2.5,-.04],[i,2.5,-.04]], QUIET)
        _line(primitives, f"grid_y_{i}", [[-2.5,i,-.04],[2.5,i,-.04]], QUIET)
        for j in range(-2, 3):
            fx, fy = field(i,j)
            _arrow(primitives, f"field_{i}_{j}", (i,j), (.28*fx,.28*fy), CYAN)
    _line(primitives, "integration_circle", [[radius*cos(2*pi*i/128), radius*sin(2*pi*i/128), .07]
                                              for i in range(129)], AMBER)
    _line(primitives, "tracer_ring", [flow(2*pi*i/128,time) for i in range(129)], MINT)
    for i in range(12):
        _sphere(primitives, f"tracer_{i}", flow(2*pi*i/12,time), .065 if i else .10,
                MINT if i else PINK)
    _line(primitives, "marked_trajectory", [flow(0,time*i/80) for i in range(81)], PINK)
    _line(primitives, "marked_radius", [[0,0,.1], flow(0,time)], PINK)
    # Parametric boundary quadrature is calculated independently of the closed
    # form. For this linear field both resulting integrands are constant.
    count = 128
    flux_terms, circulation_terms = [], []
    for i in range(count):
        theta = 2*pi*i/count
        x, y = radius*cos(theta), radius*sin(theta)
        dx, dy = -radius*sin(theta), radius*cos(theta)
        fx, fy = field(x,y)
        flux_terms.append(fx*dy-fy*dx)
        circulation_terms.append(fx*dx+fy*dy)
    flux_numeric = 2*pi/count*fsum(flux_terms)
    circulation_numeric = 2*pi/count*fsum(circulation_terms)
    area = pi*radius*radius
    flux, circulation = 2*a*area, 2*b*area
    area_factor = exp(2*a*time)
    return primitives, [
        _metric("divergence", "Divergence", 2*a, "", "Instantaneous fractional area-growth rate for this velocity field."),
        _metric("curl", "Out-of-plane curl", 2*b, "", "Counterclockwise is positive. Rigid-body angular speed is b, half this curl."),
        _metric("flux", "Outward flux: fixed circle", flux),
        _metric("circulation", "CCW circulation: fixed circle", circulation),
        _metric("area", "Tracer area ÷ initial area", area_factor, "×", "Exact flow determinant exp(2at); the integration circle remains fixed.")
    ], {}, {"divergence": 2*a, "curl_z": 2*b, "circle_area": area,
            "flux": flux, "circulation": circulation,
            "flux_quadrature": flux_numeric, "circulation_quadrature": circulation_numeric,
            "quadrature_samples": count,
            "flux_residual": abs(flux_numeric-flux),
            "circulation_residual": abs(circulation_numeric-circulation),
            "flow_radius": radius*exp(a*time), "flow_angle": b*time,
            "flow_area_factor": area_factor, "marked_tracer": flow(0,time),
            "arrow_scale": .28}, [
        "Cyan velocity arrows use one common display scale 0.28; they are not normalized independently. Their lengths remain comparable.",
        "The amber disk boundary is fixed at radius R. The mint ring is a separate set of moving fluid tracers. Flux/circulation refer to amber; area growth refers to mint.",
        "This field has exact flow X(t)=exp(at)R(bt)X(0), so the tracer picture has no numerical ODE-step error. Counterclockwise b>0 is positive rotation.",
        "The 128-point parametric boundary sums independently check the analytic flux and circulation. Constant integrands make this an especially clean Green's-theorem example, not a test of quadrature accuracy on arbitrary fields.",
        "Changing R changes total flux and circulation in proportion to area; the local divergence and curl stay fixed. One rotating marker reveals motion a perfectly unmarked circle would hide."]


MODELS = {"probability": _probability, "least_squares": _least_squares,
          "vector_field": _vector_field}
